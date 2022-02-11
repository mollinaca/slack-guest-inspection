#!/usr/bin/env python3
import configparser
import csv
import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse


def printr(message: str):
    print(message, "\r", end="")
    return 0


def printc(message: str, i: int):
    if i % 4 == 0:
        x = "|"
    elif i % 4 == 1:
        x = "/"
    elif i % 4 == 2:
        x = "-"
    elif i % 4 == 3:
        x = "\\"
    else:
        x = "|"

    print(message + x, "\r", end="")
    return 0


def loadconf() -> str:
    cfg = configparser.ConfigParser()
    cfg_file = os.path.dirname(__file__) + "/config.ini"
    cfg.read(cfg_file)
    token = cfg["slack"]["token"]
    return token


class Exec_api:
    def exec(self, req):
        """
        explanation:
            exec Slack API
        Args:
            req: urllib request object
        Return:
            body: Json object (dict)
        正常に完了した場合は Responsbody(json) を返す
        失敗した場合は、エラーjson(dict) を返す
        {"ok": false, "err":{"code": $err.code, "reason": $err.reason}}
        """
        body = {"ok": False}

        try:
            with urllib.request.urlopen(req) as res:
                body = json.loads(res.read().decode("utf-8"))
        except urllib.error.HTTPError:
            time.sleep(61)
            try:
                with urllib.request.urlopen(req) as res:
                    body = json.loads(res.read().decode("utf-8"))
            except urllib.error.HTTPError as err:
                err_d = {"reason": str(err.reason), "code": str(err.code)}
                body = {"ok": False, "err": err_d}

        except urllib.error.URLError:
            time.sleep(11)
            try:
                with urllib.request.urlopen(req) as res:
                    body = json.loads(res.read().decode("utf-8"))
            except urllib.error.URLError as err:
                err_d = {"reason": str(err.reason)}
                body = {"ok": False, "err": err_d}

        return body


class Api:
    def api_test(self):
        """
        https://api.slack.com/methods/api.test
        """
        url = "https://slack.com/api/api.test"
        req = urllib.request.Request(url)
        api = Exec_api()
        body = api.exec(req)
        return body

    def auth_test(self, token: str):
        """
        https://api.slack.com/methods/auth.test
        """
        url = "https://slack.com/api/auth.test"
        params = {"token": token}
        req = urllib.request.Request(
            "{}?{}".format(url, urllib.parse.urlencode(params))
        )
        api = Exec_api()
        body = api.exec(req)
        return body

    def d_users_list(self, token: str, offset: str = None):
        url = "https://slack.com/api/discovery.users.list"
        url = url + "?token=" + token + "&limit=100&include_deleted=false"
        if offset:
            url = url + "&offset=" + offset
        req = urllib.request.Request(url)
        api = Exec_api()
        body = api.exec(req)
        return body

    def d_users_conversations(self, token: str, id: str, offset: str = None):
        url = "https://slack.com/api/discovery.user.conversations"
        url = url + "?token=" + token + "&user=" + id
        if offset:
            url = url + "&offset=" + offset
        req = urllib.request.Request(url)
        api = Exec_api()
        body = api.exec(req)
        return body


def get_all_multiguests(token: str) -> list:
    """
    list all Multi-Channel Guests "id", "name" and "teams"
    """
    ret = []
    api = Api()

    i = 1
    res = api.d_users_list(token)
    for user in res["users"]:
        if user["is_restricted"] and not user["is_ultra_restricted"]:
            ret.append(
                [
                    user["teams"],
                    user["id"],
                    user["name"],
                    user["profile"]["email"],
                ]
            )

    if "offset" in res:
        offset = res["offset"]

        while offset:
            time.sleep(1)
            i += 1
            printc("[step1] : get all multiguests ", i)
            res = api.d_users_list(token, offset)
            for user in res["users"]:
                if user["is_restricted"] and not user["is_ultra_restricted"]:
                    ret.append(
                        [
                            user["teams"],
                            user["id"],
                            user["name"],
                            user["profile"]["email"],
                        ]
                    )
            if "offset" in res:
                offset = res["offset"]
            else:
                offset = False

    return ret


def inspection_guest(token: str, id: str) -> (bool, list):
    """
    Check to see if all Multi-Channel-Guests can be changed to Single-Channel-Guests.
    """
    cnt = 0
    api = Api()
    res = api.d_users_conversations(token, id)
    channels = []

    # count public/private channels not im/mpim
    for channel in res["channels"]:
        if (  # public channel
            (not channel["is_private"])
            and (not channel["is_im"])
            and (not channel["is_mpim"])
        ) or (  # private channel
            channel["is_private"]
            and (not channel["is_im"])
            and (not channel["is_mpim"])
        ):
            cnt += 1

    if "offset" in res:
        offset = res["offset"]
        while offset:
            res = api.d_users_conversations(token, id)

            # count more public/private channels not im/mpim
            for channel in res["channels"]:
                if (  # public channel
                    (not channel["is_private"])
                    and (not channel["is_im"])
                    and (not channel["is_mpim"])
                ) or (  # private channel
                    channel["is_private"]
                    and (not channel["is_im"])
                    and (not channel["is_mpim"])
                ):
                    cnt += 1
                else:
                    channels.append(channel["id"])

            if "offset" in res:
                offset = res["offset"]
            else:
                offset = False

    if cnt <= 1:
        return True, channels
    else:
        return False, channels


def main():
    TOKEN = loadconf()
    OUTPUT = [["team_id", "user_id", "user_name", "user_email"]]
    OUTPUT_FILE = "OUTPUT.csv"

    printr("[step1] : get all multiguests")
    guests = get_all_multiguests(TOKEN)
    print("[step1] : get all multiguests -> done")

    cnt_guests = str(len(guests))
    i = 0

    printr("[step2] : inspection each guest")
    for team, id, name, email in guests:
        i += 1
        printr("[step2] : inspection each guest  " + str(i) + "/" + cnt_guests)

        time.sleep(1)
        ret = inspection_guest(TOKEN, id)
        if ret[0]:
            OUTPUT.append([team, id, name, email])
    print("[step2] : inspection each guest -> done")

    printr("[step3] : make output csv")
    with open(OUTPUT_FILE, "w") as f:
        writer = csv.writer(f)
        for x in OUTPUT:
            writer.writerow(x)
    print("[step3] : make output csv -> done")


if __name__ == "__main__":
    main()
