#!/usr/bin/env python3

import os
import sys
import shutil
import tarfile
import environment as env
import subprocess
from tornado.log import enable_pretty_logging

enable_pretty_logging()


def get_logger(logger):
    if logger is None:
        from tornado.log import app_log
        logger = app_log
    return logger


def subset(uid, watershed_file, ids, outdir, logger=None):
    """
    function that runs all subsetting functions for PFCONUS 1.0
    """

    logger = get_logger(logger)

    logger.info(f'IDs: {ids}')
    logger.info(f'SHAPEFILE: {watershed_file}')
    logger.info(f'PATH EXISTS: {os.path.exists(watershed_file)}')

    # run the subsetting functions
    clip_inputs(watershed_file, ids, outdir, logger=logger)
    pfsol_file = subset_domain(watershed_file, ids, outdir, logger=logger)
    extract_clm(watershed_file, ids, outdir, logger=logger)
    create_tcl(pfsol_file, outdir, logger=logger)

    # compress the outputs and clean temporary directory
    fpath = os.path.join(env.output_dir, uid)
    outname = f'{uid}.tar.gz'
    outpath = f'{os.path.dirname(outdir)}/{outname}'
    with tarfile.open(outpath, "w:gz") as tar:
        tar.add(fpath, arcname=os.path.basename(fpath))
    shutil.rmtree(fpath)

    return dict(message='PF-CONUS 1.0 subsetting complete',
                filepath=f'/data/{outdir}',
                status='success')


def clip_inputs(watershed_file, ids, outdir, logger=None):
    logger = get_logger(logger)

    files_to_clip = [env.pfslopex,
                     env.pfslopey,
                     env.pfgrid,
                     env.pfpress]
    for fclip in files_to_clip:
        logger.info(f'Clipping inputs - {fclip}')
        name = os.path.basename(fclip)
        ofile = os.path.join(outdir, name)
        logger.info(f'OUTFILE: {ofile}')
        cmd = [sys.executable,
               'Clip_Inputs/clip_inputs.py',
               '-i', fclip,
               '-out_name', ofile,
               '-pfmask', env.pfmask,
               'shapefile',
               '-shp_file', watershed_file,
               '-att', 'ID',
               '-id']
        cmd.extend(ids)
        run_cmd(cmd)

    return dict(message='clip_inputs completed',
                filepath=f'/data/{outdir}',
                status='success')


def subset_domain(watershed_file, ids, outdir, logger=None):
    logger = get_logger(logger)

    logger.info('Subsetting Domain Files')
    pfsol_ofile = os.path.join(outdir, 'subset')
    cmd = [sys.executable,
           'Create_Subdomain/subset_domain.py',
           '-out_name', pfsol_ofile,
           '-pfmask', env.pfmask,
           '-pflakesmask', env.pflakesmask,
           '-pflakesborder', env.pflakesborder,
           '-pfbordertype', env.pfbordertype,
           '-pfsinks', env.pfsinks,
           'shapefile',
           '-shp_file', watershed_file,
           '-att', 'ID',
           '-id']
    cmd.extend(ids)
    run_cmd(cmd)
    
    return pfsol_ofile


def extract_clm(watershed_file, ids, outdir, logger=None):
    logger = get_logger(logger)

    logger.info('Extract CLM Lat/Lon')
    latlon_ofile = os.path.join(outdir, 'latlon.txt')
    cmd = [sys.executable,
           'CLM/domain_extract_latlon.py',
           '-shp_file', watershed_file,
           '-id']
    cmd.extend(ids)
    cmd.extend(['-att', 'ID',
                '-pfmask', env.pfmask,
                '-out_name', latlon_ofile])
    run_cmd(cmd)

    # Create vsgm LatLon
    logger.info('Extract vsgm Lat/Lon')
    ofile = os.path.join(outdir, 'drv_vegm.dat')
    cmd = [sys.executable,
           'CLM/create_vegm_latlon.py',
           '-input_igbp', env.gbpl,
           '-input_latlon', latlon_ofile,
           '-out_name', ofile]
    run_cmd(cmd)


def create_tcl(pfsol_file, outdir, logger=None):
    logger = get_logger(logger)

    logger.info('Creating TCL Script')
    cmd = [sys.executable,
           'Make_Tcl/generate_tcl_script.py',
           '-pfsol', f'{pfsol_file}.pfsol',
           '-s', os.path.join(outdir, 'slope'),
           '-t', env.pftemplate,
           '-r', os.path.join(outdir, 'cuahsi_subset'),
           '-a', outdir]
    run_cmd(cmd)


def run_cmd(cmd):
    logger = get_logger(None)
    p = subprocess.Popen(cmd,
                         cwd=env.pfexedir,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         env=os.environ.copy())
    output = p.stdout.read().decode('utf-8')
    if output != '':
        logger.info(output)
