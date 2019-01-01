from __future__ import division
import traceback
from os.path import join, basename, dirname
from time import time
import multiprocessing
import json
import os
import io
import requests
import random
import logging
import pycurl
from util import get_tld_or_host
from warcio.archiveiterator import ArchiveIterator
from urlparse import urlparse, urljoin

BASE_CC_URL = "https://commoncrawl.s3.amazonaws.com/"
CPU_COUNT = multiprocessing.cpu_count()

logger = logging.getLogger('extractor')
hdlr = logging.FileHandler('link_extracter_cc.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)

ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


def get_abs_link(href, top_url):
    try:
        return urljoin(top_url, href)
    except ValueError:
        pass
    """parsed_url = urlparse(href)
    if parsed_url.scheme not in ["http", "https"]:
        if href.startswith("//") or not parsed_url.netloc:  # relative URLs
            href = urljoin(top_url, href)
        else:
            raise ValueError("Unexpected link: %s %s" % (href, top_url))
    return href"""


def remove_white_space(text):
    """This is specifically to write to csv file."""
    return text.strip().replace("\r", "").replace("\n", "").replace("\t", "")


def sanitize_link(href):
    # some sites link to both site.com/privacy and site.com/privacy/
    href = href.rstrip('/').strip()
    return remove_white_space(href)


def is_http_link(href):
    try:
        scheme = urlparse(href).scheme
    except ValueError:
        return False
    if not href.startswith("tel:") and\
            (scheme in ["http", "https"] or not scheme):
        return True


def find_privacy_policy_link(links, top_level_url):
    non_policy_links = []
    for link in links:
        if ("path" not in link or
            "text" not in link or
                link['path'] != 'A@/href'):
            continue

        href = link["url"]
        if not href or href == "#":
            continue

        link_text = link["text"].strip()
        link_text_lower = link_text.lower()
        if not ("privacy policy" in link_text_lower or
                # lowercase "privacy" is unlikely to be a policy link
                link_text in ["Privacy", "PRIVACY"] or
                # privacy and data use policy, privacy and cookie policy
                ("privacy" in link_text_lower and
                 "policy" in link_text_lower)):
            if is_http_link(href):
                # we don't want javascript, mailto, tel links
                non_policy_links.append(href)
            continue
        href = sanitize_link(href)
        link_text = remove_white_space(link_text)
        abs_href = get_abs_link(href, top_level_url)
        non_policy_href = None
        if non_policy_links:
            non_policy_href = random.choice(non_policy_links)
            non_policy_href = sanitize_link(non_policy_href)
            non_policy_href = get_abs_link(non_policy_href, top_level_url)

        # links.add(href)
        return abs_href, link_text, non_policy_href
    return None, None, None


def extract_policy_links_from_warc():
    #try:
    #    warc_path = fetch_url(warc_url, "../ccdata")
    #except Exception as e:
    #    logger.error("Error while fetching the file %s %s" % (warc_url, e))
    #    return 0

    # this is not a unique id
    record_cnt = 0
    page_cnt = 0
    t0 = time()
    # TODO: this should be based on PS+1
    # otherwise we have many links due to subdomains
    domain_links = {}

    # iterate through files here
    i = 0
    directory = 'warc'
    for warc_file in os.listdir(directory):
        warc_path = os.path.join(directory, warc_file)
        out_csv_path = join(dirname(dirname(warc_path)), "warc_csv_out", "%s.csv" % basename(warc_path))
        
        warc_id = i
        i += 1

        print(warc_path)

        with open(warc_path, 'rb') as stream:
            for record in ArchiveIterator(stream):
                record_cnt += 1
                if record.rec_type != 'metadata':
                    continue
                page_url = record.rec_headers.get_header('WARC-Target-URI')

                # page_host = urlparse(page_url).netloc
                page_domain = get_tld_or_host(page_url)
                if page_domain in domain_links:
                    continue

                payload = record.content_stream().read()
                try:
                    page_info = json.loads(payload)
                except Exception:
                    continue
                warc_header = page_info['Envelope']['WARC-Header-Metadata']
                # other warc types: requests and metadata
                if warc_header['WARC-Type'] != 'response':
                    continue
                page_cnt += 1

                try:
                    links = page_info['Envelope']['Payload-Metadata']['HTTP-Response-Metadata']['HTML-Metadata']['Links']
                except KeyError:  # no link is found on the page/image/video
                    continue

                print("num links" + len(links))

                try:
                    href, link_text, non_policy_href =\
                        find_privacy_policy_link(links, page_url)
                except Exception as e:
                    logger.error("Error while extracting links %s %s %s %s" %
                                 (warc_id, page_url, e, traceback.format_exc()))
                    continue

                if href is not None:
                    # print page_host, href, link_text
                    domain_links[page_domain] = href
                    add_csv_line(out_csv_path, page_domain, href, link_text,
                                 non_policy_href, page_url)

    duration = time() - t0
    speed = page_cnt / duration
    logger.info("WARC %s - Finished. Pages: %s "
                "Links: %s. Time: %0.1f s. Speed: %0.1f page/s. Records : %s" %
                (warc_id, page_cnt, len(domain_links), duration,
                 speed, record_cnt))
    os.remove(warc_path)
    return len(domain_links)


def add_csv_line(out_csv_path, page_domain, href, link_text,
                 non_policy_href, page_url):
    with io.open(out_csv_path, 'a', encoding='utf-8') as f:
        try:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (page_domain, href, link_text,
                                              non_policy_href, page_url))
        except Exception as e:
            print e, page_domain, href, link_text, non_policy_href, page_url


def extract_policy_links_from_warc_files(warc_paths):
    p = multiprocessing.Pool(CPU_COUNT)
    total_n_links = 0
    warc_urls = [BASE_CC_URL + l.rstrip() for l in open(warc_paths).readlines()]
    # print "Will process", len(warc_urls), "warc URLs"
    t0 = time()
    n_warcs = len(warc_urls)
    logger.info("Will process %s warc URLs" % n_warcs)
    warcs_processed = 0
    for n_links in p.imap(extract_policy_links_from_warc, warc_urls):
        warcs_processed += 1
        total_n_links += n_links
        duration = time() - t0
        logger.info("Total links found: %s duration: %0.1f - Progress: %d / %d"
                    % (total_n_links, duration, warcs_processed, n_warcs))
    p.close()


def fetch_url(url, out_dir):
    local_filename = join(out_dir, url.split('/')[-1])
    if os.path.isfile(local_filename):
        print "already downloaded", local_filename
        return local_filename
    t0 = time()
    with open(local_filename, 'wb') as f:
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, f)
        c.perform()
        c.close()
    logger.info("Download took %0.1f sec Size: %s" % (
        (time() - t0), os.path.getsize(local_filename)))
    return local_filename


# https://stackoverflow.com/a/16696317
def download_file(url, out_dir):
    local_filename = join(out_dir, url.split('/')[-1])
    if os.path.isfile(local_filename):
        print "already downloaded", local_filename
        return local_filename
    print "Will download", url, "to", local_filename
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return local_filename


if __name__ == '__main__':
    t0 = time()
    extract_policy_links_from_warc()
    #extract_policy_links_from_warc_files("../ccdata/warc.paths")
    logger.info("Finished in %s s" % (time() - t0))
    # WARC = "/home/gacar/dev/privacy-policy/ccdata/CC-MAIN-20180419091546-20180419111546-00009.warc.wat.gz"
    # extract_policy_links_from_warc_files("../ccdata/warc.paths")
    # wat_url = "crawl-data/CC-MAIN-2018-13/segments/1521257644271.19/wat/CC-MAIN-20180317035630-20180317055630-00038.warc.wat.gz"
    # extract_policy_links_from_warc(BASE_CC_URL + wat_url)
