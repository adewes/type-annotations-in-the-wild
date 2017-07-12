import multiprocessing as mp
import requests
import json
import datetime
import time
import random
import os
import sys
import httplib
import gzip

from settings import ACCESS_TOKEN

usage = """
Usage: %s [language] [output JSON filename]

By default, the script appends to the output file.
""" % sys.argv[0]

headers = {
    'User-Agent': 'Github Scraper',
}

def establish_connection():
    print "Establishing connection in process %d..." % os.getpid()
    con = httplib.HTTPSConnection('api.github.com',443)
    return con

def smart_open(filename,*args,**kwargs):
    if filename.endswith(".gz"):
        open_func = gzip.open
    else:
        open_func = open
    return open_func(filename,*args,**kwargs)

def get_language_repos(language,since,output_file):
    try:
        while True:
            print "Getting top repositories for %s" % (language)
            con = establish_connection()
            try:
                url = '/repositories?access_token=%s&since=%d' % (ACCESS_TOKEN,since)
                con.request('GET',url,headers = headers)
                response = con.getresponse()
            except:
                print "Connection error"
                break
            if response.status == 404:
                break
            elif response.status != 200 and response.status != 403:
                print "Invalid response..."
                break
            remaining_requests = int(response.getheader('x-ratelimit-remaining'))
            reset_time = datetime.datetime.fromtimestamp(int(response.getheader('x-ratelimit-reset')))
            print "%d requests remaining..." % (remaining_requests)
            if remaining_requests == 0:
                print "Allowed requests depleted, waiting..."
                while True:
                    if reset_time < datetime.datetime.now():
                        print "Continuing!"
                        break
                    waiting_time_seconds = (reset_time-datetime.datetime.now()).total_seconds()
                    waiting_time_minutes = int(waiting_time_seconds/60)
                    waiting_time_seconds_remainder = int(waiting_time_seconds) % 60
                    print "%d minutes and %d seconds to go" % (waiting_time_minutes,waiting_time_seconds_remainder)
                    time.sleep(10)
                break
            content = response.read()
            repos = json.loads(content)
            since = max(since, max(*[repo['id'] for repo in repos]))
            if not len(repos):
                break
            output_file.write("\n".join([json.dumps(repo).strip() for repo in repos]))
    except KeyboardInterrupt as e:
        print "Keyboard interrupt..."
    except requests.exceptions.RequestException as e:
        print "Exception occured:",str(e)

if __name__ == '__main__':

        if len(sys.argv) < 3:
                print usage
                exit(-1)

        language = sys.argv[1]
        output_filename = sys.argv[2]

        running_tasks = 0

        task_list = []
        since = 0
        if os.path.exists(output_filename):
            with smart_open(output_filename,"rb") as input_file:
                last_line = None
                for line in input_file:
                    last_line = line
                if last_line:
                    repo = json.loads(last_line)
                    since = repo['id']
        with smart_open(output_filename,"ab") as output_file:
            get_language_repos(language,since,output_file)
