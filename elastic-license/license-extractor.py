#!/usr/bin/python
import csv
import urllib.request as request
import ssl
import sys


# Following structure of the input cvs is assumed: module name, version, license type, URL, packaged
reader = csv.reader(open('./logstash-5.4.csv', 'rt', encoding='UTF8'))
writer = csv.writer(open('./logstash-5.4-enriched.csv', 'wt', encoding='UTF8'), delimiter='\t')
dlq = csv.writer(open('./logstash-5.4-dlq.csv', 'wt', encoding='UTF8'))


#reader = csv.reader(open('./kibana-5.4.csv', 'rt', encoding='UTF8'))
#writer = csv.writer(open('./kibana-5.4-enriched.csv', 'wt', encoding='UTF8'), delimiter='\t')
#dlq = csv.writer(open('./kibana-5.4-dlq.csv', 'wt', encoding='UTF8'))

# Adding two additional rows - copyright and license text
headers = next(reader)
headers.append("Copyright")
headers.append("License text")
writer.writerow(headers)
dlq.writerow(headers)

# Ignore SSL
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def extract_copyright(content):
    for token in content.split("\n"):
        if ("Copyright" in token) or ("(c)" in token):
            return token
        else:
            return "Failed to extract copyright"

for row in list(reader):
    url = row[3]

    if ("://github.com" in url) or ("http://www.elastic.co/guide/en/logstash/current/index.html" in url):
        basic_url = ""
        if ("http://www.elastic.co/guide/en/logstash/current/index.html" in url):
            basic_url = url.replace("http://www.elastic.co/guide/en/logstash/current/index.html", "https://raw.githubusercontent.com")
            basic_url = basic_url + '/logstash-plugins/' + row[0]
        else:
            basic_url = url.replace('://github.com', '://raw.githubusercontent.com')

        url_list = list()
        # the most common combinations, this is really subjective
        url_list.append(basic_url + '/v' + row[1] + '/NOTICE')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/NOTICE')
        url_list.append(basic_url + '/v' + row[1] + '/NOTICE.txt')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/NOTICE.txt')
        url_list.append(basic_url + '/v' + row[1] + '/NOTICE.md')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/NOTICE.md')
        url_list.append(basic_url + '/v' + row[1] + '/LICENSE')
        url_list.append(basic_url + '/v' + row[1] + '/LICENSE.txt')
        url_list.append(basic_url + '/v' + row[1] + '/COPYING')
        url_list.append(basic_url + '/v' + row[1] + '/LICENSE.md')
        url_list.append(basic_url + '/v' + row[1] + '/COPYING.txt')
        url_list.append(basic_url + '/v' + row[1] + '/COPYING.md')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/LICENSE')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/LICENSE.txt')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/COPYING')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/COPYING.txt')
        url_list.append(basic_url + '/' + row[1] + '/LICENSE')
        url_list.append(basic_url + '/' + row[1] + '/LICENSE.txt')
        url_list.append(basic_url + '/' + row[1] + '/COPYING')
        url_list.append(basic_url + '/' + row[1] + '/COPYING.txt')
        # these less common, subjective as well
        url_list.append(basic_url + '/v' + row[1] + '/MIT-LICENSE')
        url_list.append(basic_url + '/v' + row[1] + '/MIT-LICENSE.txt')
        url_list.append(basic_url + '/v' + row[1] + '/MIT-LICENSE.md')
        url_list.append(basic_url + '/v' + row[1] + '/LICENSE-MIT')
        url_list.append(basic_url + '/v' + row[1] + '/LICENSE-MIT.txt')
        url_list.append(basic_url + '/v' + row[1] + '/LICENSE-MIT.md')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/MIT-LICENSE.txt')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/MIT-LICENSE')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/LICENSE.BSD')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/LICENSE.md')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/LICENSE-MIT')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/LICENSE-MIT.txt')
        url_list.append(basic_url + '/' + row[0] + '-' + row[1] + '/LICENSE-MIT.md')
        url_list.append(basic_url + '/' + row[1] + '/MIT-LICENSE.txt')
        url_list.append(basic_url + '/' + row[1] + '/MIT-LICENSE')
        url_list.append(basic_url + '/' + row[1] + '/LICENSE.BSD')
        url_list.append(basic_url + '/' + row[1] + '/LICENSE.md')

        license_extracted = False

        for url_variant in url_list:
            try:
                content = request.urlopen(url_variant, context=ctx).read()
                copyr = extract_copyright(content.decode('UTF-8'))
                content = content.decode('UTF-8').replace('\t', ' ').replace('\n', '')
                row.append(copyr)
                row.append(content)
                writer.writerow(row)
                license_extracted = True
                break
            # catching e.g. UnicodeDecodeError and HTTPError (e.g. when resource does not exist)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                continue
        # write to DLQ when no match
        if not license_extracted:
            print("Writing to dlq: " + url)
            dlq.writerow(row)
    else:
        dlq.writerow(row)