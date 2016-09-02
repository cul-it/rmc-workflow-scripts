#!/usr/bin/env python3

import glob
import os
import sys
import re
import argparse
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from string import Template

namespaces = {'dfxml' : 'http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML',
              'marc' : 'http://www.loc.gov/MARC21/slim'}


# NOTE TEMPORARY
inputdir = '/Users/dianne/Desktop/To Do/EmulationGoldsen/GoldsenMD'
inputoffset = 5

xml_tmpl = {'i386': 'xml-templates/qemu01.xml',
            '68k' : 'xml-templates/basiliskii01.xml',
            'ppc' : 'xml-templates/sheepshaver01.xml'}


def scrub_marc(marc):
    marc = marc.rstrip(',')
    marc = marc.rstrip(' :')
    marc = marc.rstrip(' /')
    marc = marc.rstrip('.')
    marc = marc.rstrip(',')
    return marc


def parse_md():
    conf = defaultdict(dict)

    # Adjust in production
    goldsen_files = glob.glob(os.path.join(inputdir, 'RMM', 'RMM*', 'PAFDAO', 'WORKS', '*'))

    for gf in goldsen_files:
        fullpath = gf.split(os.sep)
        rmm_num = fullpath[inputoffset+1]
        bibid = os.path.basename(gf)

        mx = glob.glob(os.path.join(gf, '*_marcxml.xml'))
        if len(mx) != 1:
            print(gf,"Missing MARCXML") # TEMPORARY WORKAROUND
            sys.exit('Unexpected number of marcxml files. Quitting.') 

        marcxml = ET.parse(mx[0]).getroot()
        record = marcxml.getchildren()[0]
        datafields = record.findall('marc:datafield', namespaces)

        sysreqs = []
        title = None
        creator = None
        alt_creator = None
        date = None

        for df in datafields:
            if df.get('tag') == '538':
                df_children = df.getchildren()
                for dfc in df_children:
                    sysreqs.append(dfc.text)
            elif df.get('tag') == '245':
                df_children = df.getchildren()
                for dfc in df_children:
                    if dfc.get('code') == 'a':
                        title = scrub_marc(dfc.text)
                    elif dfc.get('code') == 'c':
                        creator = scrub_marc(dfc.text)
            elif df.get('tag') == '100':
                df_children = df.getchildren()
                for dfc in df_children:
                    if dfc.get('code') == 'a':
                        alt_creator = scrub_marc(dfc.text)
            elif df.get('tag') == '260':
                df_children = df.getchildren()
                for dfc in df_children:
                    if dfc.get('code') == 'c':
                        date = scrub_marc(dfc.text)
                        date = date.lstrip('c')
                        date = date.strip('?')
                        date = date.strip('[')
                        date = date.strip(']')

        for di in glob.glob(os.path.join(gf, 'disk_images', '*_dfxml.xml')):
            pre_disk_image = os.path.basename(di).split('_')
            disk_image_id = '{0}_{1}'.format(bibid, pre_disk_image[1])
            dfxml = ET.parse(di).getroot()
            vols = dfxml.findall('dfxml:volume', namespaces)
            filesystems = []
            for v in vols:
                pre_filesystems = v.findall('dfxml:ftype_str', namespaces)
                for fs in pre_filesystems:
                    filesystems.append(fs.text)

            # Set up conf
            conf[disk_image_id] = {}
            conf[disk_image_id]['RMM'] = rmm_num
            conf[disk_image_id]['sysreq'] = sysreqs
            conf[disk_image_id]['filesystems'] = filesystems
            conf[disk_image_id]['title'] = title
            conf[disk_image_id]['date'] = date

            if (creator is None) and (alt_creator is None):
                conf[disk_image_id]['creator'] = ''
            elif (alt_creator is not None) and (creator is None):
                conf[disk_image_id]['creator'] = alt_creator
            elif (creator is not None):
                conf[disk_image_id]['creator'] = creator

            # TODO: Fix this when you actually have actual disk images to glob in here
            pre_diloc = glob.glob(os.path.join(gf, 'disk_images', '{0}.dd'.format(disk_image_id)))
            conf[disk_image_id]['disk_img'] = pre_diloc


    return conf

def conf2tmpl(conf_entry, outpath):
    # create empty directory for destination of templates
    # First go through conf file and figure out what's needed to be created
    for entry in conf_entry.keys():
        # Which templates do we need?
        if 'ISO9660' in conf_entry[entry]['filesystems']:
            tmpl = Template(open(xml_tmpl['i386']).read())
            towrite = open(os.path.join(outpath, '{0}_i386.xml'.format(entry)), 'w')
            tmpl = tmpl.substitute(BIBIDCDNO = entry,
                                   MARCTITLE = conf_entry[entry]['title'],
                                   EMUPATH = 'TEMPORARY://qemuFILE',
                                   ARTPATH = conf_entry[entry]['disk_img'])
            towrite.write(tmpl)
            towrite.close()


        if 'HFS' in conf_entry[entry]['filesystems']:
            pass
        
        if 'HFS+' in conf_entry[entry]['filesystems']:
            pass

# TODO: name of file to create, and string that represents the file data

def main():
# NOT NEEDED YET
    parser = argparse.ArgumentParser()
    parser.add_argument('outputdir', metavar='[output_dir]',
                        help='output directory (initially empty) for XML configuration files')
    args = parser.parse_args()

    try:
        dirtest = os.listdir(args.outputdir)
    except:
        os.makedirs(args.outputdir)
    else:
        if dirtest:
            sys.exit('Quitting: Output directory is not empty.')


    goldsenconf = parse_md()
    conf2tmpl(goldsenconf, args.outputdir)

if __name__ == "__main__":
    main()
