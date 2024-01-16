import yaml
import requests
import sys
import time
import signal

def signal_handler(sig, frame):
    print("\nEnd of program")
    sys.exit(0)

def read_yaml_file(path):
    try:
        with open(path, 'r') as file:
            try:
                yaml_file = yaml.safe_load(file)
            except yaml.YAMLError as e:
                print("Error loading file")
                sys.exit(1)
    except FileNotFoundError as e:
        print("File not found")
        sys.exit(1)
    return yaml_file

def get_domain(url):
    return url.split(':')[1].split('/')[2]

def check_health(url, method, headers, body):
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, data=body, timeout=0.7)
        else:
            response = requests.post(url, headers=headers, data=body, timeout=0.7)
        if 200 <= response.status_code < 300 and response.elapsed.total_seconds() < 0.5:
            return True
    except requests.RequestException as e:
        return False
    return False

def get_availability_percentage(file):
    total_map = {}
    up_map = {}
    start = time.time() + 15
    while True:
        for f in file:
            domain = get_domain(f['url'])
            if domain not in total_map:
                total_map[domain] = 0
                up_map[domain] = 0
            if check_health(f['url'], f.get('method','GET'), f.get('heaaders', None), f.get('body', None)):
                up_map[domain] += 1
            total_map[domain] += 1
        for domain in total_map.keys():
            print(domain + " has " + str(round(up_map[domain]*100/total_map[domain])) + "% availability percentage")
        while(time.time() <  start):
            continue
        start += 15

def main():
    signal.signal(signal.SIGINT, signal_handler)
    if(len(sys.argv) < 2):
        print("Please specify a filename")
        sys.exit(1)
    filename = sys.argv[1]
    file = read_yaml_file(filename)
    get_availability_percentage(file)

if __name__ == "__main__":
    main()