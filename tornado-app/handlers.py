#!/usr/bin/env python3

import os
import json
import time
import tornado.auth
import tornado.web
import uuid
import subprocess
import hashlib
from urllib.parse import urljoin
from datetime import datetime
import bbox
import transform
import urllib.parse
import xml.etree.ElementTree as ET
import environment as env

import multiprocessing

from tornado import gen 
from tornado.httpclient import AsyncHTTPClient

from tornado.log import app_log, gen_log, access_log, LogFormatter
from tornado.log import enable_pretty_logging
enable_pretty_logging()


import jobs
executor = jobs.BackgroundWorker()

import sqldata
sql = sqldata.Connect(env.sqldb)
sql.build()

import subset


class RequestHandler(tornado.web.RequestHandler):
    errors = []

    def get_or_error(self, argname, strip=True):
        """
        This function gets a REST input argument or returns an error message if the argument is not found
        Arguments:
        argname -- the name of the argument to get
        strip -- indicates if the whitespace will be stripped from the argument
        """
        arg = self.get_argument(argname, default=None, strip=strip)
        if arg is None:
            error = 'Could not find required parameter "%s"' % argname
            self.render("index.html", header=header, args=args, error=error)
        return arg

    def get_arg_value(self, argname, isrequired, strip=True):
        arg = self.get_argument(argname, default=None, strip=strip)
        if arg is None and isrequired:
            error = 'Could not find required parameter "%s"' % argname
            self.errors.append(error)
        return arg
   
    def check_for_errors(self):
        response = False
        if len(self.errors) > 0:
            response = dict(message="invalid arguments", status="fail")
        return response


class IndexHandler(RequestHandler, tornado.auth.OAuth2Mixin):
    def get(self):
        self.render("index.html", title="CUAHSI Subsetter v0.1")

    def post(self):
        ulat = self.get_argument('ulat')
        llat = self.get_argument('llat')
        ulon = self.get_argument('ulon')
        llon = self.get_argument('llon')
        hucs = self.get_argument('hucs')

        if '' in [ulat, ulon, llat, llon]:
            self.render("index.html",
                        title="CUAHSI Subsetter v0.1",
                        msg='ERROR: Missing required input')

        # build GET url for subsetting
        query = f'llat={llat}&llon={llon}&ulat={ulat}&ulon={ulon}&hucs={hucs}'
        self.redirect('nwm/v1_2_2/subset?%s' % query)


class LccBBoxFromHUC(RequestHandler):
    """
    Get BBOX in Lambert Conformal Conic for given a HUC ID.
    """

    def get(self):
        hucstring = self.get_arg_value('hucID', True)
        hucs = hucstring.split(',')
        huclevels = [len(huc) for huc in hucs]
        box = bbox.get_bbox_from_hucs(huclevels, hucs)
    
        response = dict(hucID=hucs,
                        hucLevel=huclevels,
                        bbox=box)

        self.write(json.dumps(response))


class SubsetNWM122(RequestHandler):
    """
    Subsetting endpoint for NWM v1.2.2
    """

    @tornado.gen.coroutine
    def get(self):
        global executor

        app_log.debug('SubsetNWM122 function')

        # collect rest arguments
        llat = self.get_arg_value('llat', True)
        llon = self.get_arg_value('llon', True)
        ulat = self.get_arg_value('ulat', True)
        ulon = self.get_arg_value('ulon', True)
        hucs = self.get_arg_value('hucs', True).split(',')

        app_log.debug('submitted bbox: (%s, %s, %s, %s) ' %
                      (llat, llon, ulat, ulon))
       
        # calculate unique hash based on bbox
        hasher = hashlib.sha1()
        hasher.update(str([llon, llat, ulon, ulat]).encode('utf-8'))
        uid = hasher.hexdigest()
       
        # check if this job has been executed previously
        app_log.debug('Checking if job exists')
        res = sql.get_job_by_guid(uid)
        app_log.debug(res)

        # submit the job
        if len(res) == 0:

            # submit the subsetting job
            args = (uid, llat, llon, ulat, ulon, hucs)
            uid = executor.add(uid, subset.subset_nwm_122, *args)

        # redirect to status page for this job
        app_log.debug('redirecting to status page')
        self.redirect('/status/%s' % uid)


class Status(RequestHandler):
    @gen.coroutine
    def get(self, jobid=None):
        if jobid is None:
            http_client = AsyncHTTPClient()
            host_url = "{protocol}://{host}".format(**vars(self.request))
            url = host_url + '/jobs'
            response = yield http_client.fetch(url)
            data = json.loads(response.body)
            self.render('admin_status.html', jobs=data) 
        else:
            self.render('status.html')


class Job(RequestHandler):
    @tornado.web.asynchronous
    def get(self, jobid=None):
        if jobid is None:
            self.get_all_jobs()
        else:
            self.get_job_by_id(jobid)

    @tornado.web.asynchronous
    def get_all_jobs(self):
        response = []
        jobs = sql.get_jobs()
        if jobs is None:
            response = []
        else:
            for job in jobs:
                fpath = self.get_file_url(job[2])
              
                # format dates nicely
                st = job[3]
                et = job[4]
                if st is not None:
                    st = datetime.strptime(st, '%Y-%m-%d %H:%M:%S.%f') \
                                 .strftime('%m-%d-%Y %H:%M:%S')
                if et is not None:
                    et = datetime.strptime(et, '%Y-%m-%d %H:%M:%S.%f') \
                                 .strftime('%m-%d-%Y %H:%M:%S')

                # build response object
                response.append(dict(id=job[0],
                                     status=job[1],
                                     file=fpath,
                                     start=st,
                                     end=et))
        # return serialized data
        self.write(json.dumps(response))
        self.finish()

    @tornado.web.asynchronous
    def get_job_by_id(self, jobid):
        response = None

        # todo: remove this loop and replace with a sqldata.get_job_by_guid.
        jobs = sql.get_jobs()
        for job in jobs:
            if jobid == job[0]:
                fpath = self.get_file_url(job[2])

                # format dates nicely
                st = job[3]
                et = job[4]
                if st is not None:
                    st = datetime.strptime(st, '%Y-%m-%d %H:%M:%S.%f') \
                                 .strftime('%m-%d-%Y %H:%M:%S')
                if et is not None:
                    et = datetime.strptime(et, '%Y-%m-%d %H:%M:%S.%f') \
                                 .strftime('%m-%d-%Y %H:%M:%S')

                # build response object
                response = dict(id=job[0],
                                status=job[1],
                                file=fpath,
                                start=st,
                                end=et)
                continue
        if response is None:
            response = dict(message='Job Not Found',
                            status='error')

        self.write(json.dumps(response))
        self.finish()

    def get_file_url(self, relative_file_path):
        if relative_file_path.strip() != '':
            host_url = "{protocol}://{host}".format(**vars(self.request))
            return host_url + relative_file_path
        return None


class About(RequestHandler):
    @gen.coroutine
    def get(self):
        self.render('about.html')


class Help(RequestHandler):
    @gen.coroutine
    def get(self):
        self.render('help.html')


class Api(RequestHandler):
    @gen.coroutine
    def get(self):
        self.render('api.html')

class GettingStarted(RequestHandler):
    @gen.coroutine
    def get(self):
        self.render('getting-started.html')
