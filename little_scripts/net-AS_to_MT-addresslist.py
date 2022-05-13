import requests
import re
import netaddr


def get_data_ipinfo(AS: str) -> dict:
    url = f"https://ipinfo.io/{AS}"
    result = {}
    try:
        session = requests.Session()
        source = session.get(url)
    except:
        result["status"] = False
    else:
        result["status"] = source.status_code
        print(source.text)
        tmp = re.findall(r"(\d{,3}\.\d{,3}\.\d{,3}\.\d{,3}/\d{,2})", source.text)
        result["data"] = tmp
    return result


def get_data_input(comment="") -> dict:
    result = {"status": True, "data": {}}
    for line in iter(input, ""):
        if comment:
            netblock, *_ = line.strip().split("\t")
            result["data"].setdefault(comment, []).append(netblock)
        else:
            netblock, company, *_ = line.strip().split("\t")
            result["data"].setdefault(company, []).append(netblock)
    return result


def main():
    addresslist = "block_enemy"
    # get_data_ipinfo("AS32934")
    source = get_data_input("facebook")
    if not source["status"]:
        quit()
    for comment,addresses in source["data"].items():
        # print(comment, addresses)
        for address in netaddr.cidr_merge(addresses):
            print(f'/ip firewall address-list add address="{address}" list="{addresslist}" comment="{comment}"')


if __name__ == '__main__':
    main()
