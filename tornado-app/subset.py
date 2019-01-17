#!/usr/bin/env python3

import os
import sys
import json
import subprocess
import transform
import tarfile
import shutil
import environment as env


def subset_nwm_122(uid, ymin, xmin, ymax, xmax, logger=None):
    
    if logger is None:
        from tornado.log import app_log
        logger = app_log

    # list object to store stdout info for debugging
    stdout = []
    stdout.append('UID: %s\n'
                  'xmin: %s\n'
                  'ymin : %s\n'
                  'xmax : %s\n'
                  'ymax : %s\n\n' % (uid, str(xmin), str(ymin),
                                     str(xmax), str(ymax)))

    geofile = env.geofile
    bbox = (float(xmin),
            float(ymin),
            float(xmax),
            float(ymax))

#    # check that bbox is valid
#    logger.info('validating bounding box')
#    if (ymin > ymax) | (xmin > xmax):
#        logger.error('invalid bounding box')
#        return

    # TODO: check bbox size

    # run R script and save output as random guid
    logger.info('begin NWM v1.2.2 subsetting %s' % (uid) )

    cmd = ['Rscript',
           'subset_domain.R',
           uid,
           str(ymin),
           str(ymax),
           str(xmin),
           str(xmax)]
    print(' '.join(cmd))
    p = subprocess.Popen(cmd,
                         cwd=os.path.join(os.getcwd(), 'r-subsetting'),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

#    for line in iter(p.stdout.readline, b''):
#        l = line.decode('utf-8').rstrip()
#        if 'std' in l:
#            l = l.replace('std:', '\n')
#            stdout.append(l)
#        print(l, flush=True)
#    p.stdout.close()
    return_code = p.wait()
    

    if not return_code == 0:
        msg= 'The process call "{}" returned with code {}, an error ' \
             'occurred.'.format(list(cmd), return_code)
        logger.error('subsetting failed %s: %s' % (uid, msg) )
        response = dict(message=msg, status='error')
        return response

    logger.info('subsetting complete %s' % (uid) )

    # compress the results
    fpath = os.path.join('/tmp', uid)
    outname = '%s.tar.gz' % uid
    with tarfile.open('/tmp/'+outname,  "w:gz") as tar:
        tar.add(fpath, arcname=os.path.basename(fpath))
    shutil.rmtree(fpath)
    logger.info('finished compressing results %s' % (uid)) 

    response = dict(message='file created at: /tmp/data/%s' % outname,
                        filepath='/data/%s' % outname,
                        status='success')
    return response



#def subset_by_bbox(uid, llat, llon, ulat, ulon):
#
#    # list object to store stdout info for debugging
#    stdout = []
#    stdout.append('UID: %s\n'
#                  'llat (WGS84): %s\n'
#                  'llon (WGS84): %s\n'
#                  'ulat (WGS84): %s\n'
#                  'ulon (WGS84): %s\n\n' %(uid, str(llat), str(llon), str(ulat), str(ulon)))
#
#    geofile = '/home/acastronova/www.nco.ncep.noaa.gov/pmb/codes/nwprod/nwm.v1.2.2/parm/domain/geo_em.d01_1km.nc'
#    bbox = (float(llon),
#            float(llat),
#            float(ulon),
#            float(ulat))
#    coords = [(bbox[0], bbox[1]), # lower left
#              (bbox[2], bbox[3]), # upper left
#              (bbox[2], bbox[3]), # upper right
#              (bbox[0], bbox[1])] # lower right
#    transformed = transform.proj_to_coord(coords)
#    xs = [t[0] for t in transformed]
#    ys = [t[1] for t in transformed]
#    ysouth= min(ys)
#    ynorth= max(ys)
#    xwest = min(xs)
#    xeast=  max(xs)
#    stdout.append('Transformed (WGS -> Lambert Conformal Conic Variant)\n'
#                  'llat (LCC, m): %s\n'
#                  'llon (LCC, m): %s\n'
#                  'ulat (LCC, m): %s\n'
#                  'ulon (LCC, m): %s\n\n' %(str(ysouth), str(xwest), str(ynorth), str(xeast)))
#
#    # check that bbox is valid
#    print('validating bounding box')
#    if (ysouth > ynorth) | (xwest > xeast):
#        print('invalid bounding box')
#
#    # run R script and save output as random guid
#    print('invoking subsetting algorithm')
#
#    cmd = ['Rscript',
#           'subset_domain.R',
#           uid,
#           str(ysouth),
#           str(ynorth),
#           str(xwest),
#           str(xeast)]
#    print(' '.join(cmd))
#    p = subprocess.Popen(cmd,
#                         cwd=os.path.join(os.getcwd(),'r-subsetting'),
#                         stdout=subprocess.PIPE,
#                         stderr=subprocess.STDOUT)
#
#    for line in iter(p.stdout.readline, b''):
#        l = line.decode('utf-8').rstrip()
#        if 'std' in l:
#            l = l.replace('std:', '\n')
#            stdout.append(l)
#    p.stdout.close()
#    return_code = p.wait()
#
#    if not return_code == 0:
#        response = dict(message =
#            'The process call "{}" returned with code {}, an error '
#            'occurred.'.format(list(cmd), return_code),
#                       status='error')
#    else:
#        fpath = os.path.join('/tmp', uid) 
#
#        # save the stdout from the subsetting 
#        with open(os.path.join(fpath, 'stdout.txt'), 'w') as f:
#            for line in stdout:
#                f.write(line)
#               
#        outname = '%s.tar.gz' % uid
#
#        # compress the results
#        outname = '%s.tar.gz' % uid
#        with tarfile.open('/tmp/'+outname,  "w:gz") as tar:
#            tar.add(fpath, arcname=os.path.basename(fpath))
#        print('removing dir')
#        shutil.rmtree(fpath)
#
#        response = dict(message='file created at: /tmp/data/%s' % outname,
#                        filepath='/data/%s' % outname,
#                        status='success')
#
#    return response
#
#
#def mute():
#    sys.stdout = open(os.devnull, 'w') 
