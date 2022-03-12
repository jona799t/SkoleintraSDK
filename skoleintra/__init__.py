import json
import httpx
import requests
import urllib
import ssl
from urllib3 import poolmanager
from bs4 import BeautifulSoup
from unilogin import Unilogin

class TLSAdapter(requests.adapters.HTTPAdapter): #https://stackoverflow.com/questions/61631955/python-requests-ssl-error-during-requests
    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx)

class Skoleintra:
    def __init__(self, url, type="elev", brugernavn="", adgangskode=""):
        self.success = False

        self.session = requests.session()
        self.session.mount('https://', TLSAdapter())
        self.uniloginClient = Unilogin(brugernavn=brugernavn, adgangskode=adgangskode)

        self.defaultHeaders = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        }

        if url[-1] == "/":
            url = url[:-1]
        if "https://" not in url and "http://" not in url:
            url = "https://" + url
        baseUrl = url.split("://")[1].split("/")[0]
        if type == "elev":
            url = f"{url}/Account/IdpLogin?role=Student&partnerSp=urn%3Aitslearning%3Ansi%3Asaml%3A2.0%3A{baseUrl}"

        resp = self.session.get(url, headers=self.defaultHeaders, allow_redirects=False)
        cookies = {"Pool": resp.cookies["Pool"], "SsoSessionId": resp.cookies["SsoSessionId"], "__RequestVerificationToken": resp.cookies["__RequestVerificationToken"]} #, "HasPendingSSO": resp.cookies["HasPendingSSO"]
        href = f"https://{baseUrl}" + BeautifulSoup(resp.text, 'html.parser').find("a", {"class": "ccl-button sk-button-light-green sk-font-icon sk-button-text-only sk-uni-login-button"}).get("href")

        headers = self.defaultHeaders
        headers["cookie"] = f"Pool={cookies['Pool']}; SsoSessionId={cookies['SsoSessionId']}; __RequestVerificationToken={cookies['__RequestVerificationToken']}"
        resp = self.session.get(href, headers=headers, allow_redirects=False)
        location = resp.headers["location"]

        authUrl = self.uniloginClient.login(href=location, referer=baseUrl)

        resp = self.session.get(authUrl, headers=self.defaultHeaders, allow_redirects=False)
        cookies["SsoSelectedSchool"] = resp.cookies["SsoSelectedSchool"]
        cookies["UserRole"] = resp.cookies["UserRole"]
        cookies["Language"] = resp.cookies["Language"]
        cookies[".AspNet.SSO.ApplicationCookie"] = resp.cookies[".AspNet.SSO.ApplicationCookie"]
        location = resp.headers["location"]

        headers = self.defaultHeaders
        headers["cookie"] = f"SsoSelectedSchool={cookies['SsoSelectedSchool']}; Language={cookies['Language']}; .AspNet.SSO.ApplicationCookie={cookies['.AspNet.SSO.ApplicationCookie']}"
        resp = self.session.get(location, headers=headers, allow_redirects=False)

        html = BeautifulSoup(resp.text, 'html.parser')
        href = html.find('form').get('action')
        samlResponse = [html.find("input", {"name": "SAMLResponse"}).get("name"), html.find("input", {"name": "SAMLResponse"}).get("value")]
        replayState = [html.find("input", {"name": "RelayState"}).get("name"), html.find("input", {"name": "RelayState"}).get("value")]

        payload = f"{samlResponse[0]}={urllib.parse.quote_plus(samlResponse[1])}&{replayState[0]}={urllib.parse.quote_plus(replayState[1])}"
        headers = self.defaultHeaders
        headers["content-length"] = str(len(payload))
        headers["content-type"] = "application/x-www-form-urlencoded"
        headers["cookie"] = f"Pool={cookies['Pool']}; SsoSessionId={cookies['SsoSessionId']}; __RequestVerificationToken={cookies['__RequestVerificationToken']}; SsoSelectedSchool={cookies['SsoSelectedSchool']}; UserRole={cookies['UserRole']}; Language={cookies['Language']}; .AspNet.SSO.ApplicationCookie={cookies['.AspNet.SSO.ApplicationCookie']}"

        resp = self.session.post(href, headers=headers, data=payload, allow_redirects=False)
        cookies[".AspNet.ApplicationCookie"] = resp.cookies[".AspNet.ApplicationCookie"]
        self.cookies = cookies
        self.success = True

    def getWeeklyplans(self, week, year):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": f"Pool={self.cookies['Pool']}; SsoSessionId={self.cookies['SsoSessionId']}; __RequestVerificationToken={self.cookies['__RequestVerificationToken']}; SsoSelectedSchool={self.cookies['SsoSelectedSchool']}; UserRole={self.cookies['UserRole']}; Language={self.cookies['Language']}; .AspNet.SSO.ApplicationCookie={self.cookies['.AspNet.SSO.ApplicationCookie']}; .AspNet.ApplicationCookie={self.cookies['.AspNet.ApplicationCookie']}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        }
        resp = self.session.get(f"https://{self.cookies['SsoSelectedSchool']}/student/weeklyplans/list/item/class/{week}-{year}", headers=headers)

        weeklyplan = json.loads(BeautifulSoup(resp.text, 'html.parser').find("div", {"id": "root"}).get("data-clientlogic-settings-weeklyplansapp"))
        return weeklyplan

    async def getWeeklyplansAsync(self, week, year):
        if len(str(week)) == 1:
            week = f"0{week}"
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": f"Pool={self.cookies['Pool']}; SsoSessionId={self.cookies['SsoSessionId']}; __RequestVerificationToken={self.cookies['__RequestVerificationToken']}; SsoSelectedSchool={self.cookies['SsoSelectedSchool']}; UserRole={self.cookies['UserRole']}; Language={self.cookies['Language']}; .AspNet.SSO.ApplicationCookie={self.cookies['.AspNet.SSO.ApplicationCookie']}; .AspNet.ApplicationCookie={self.cookies['.AspNet.ApplicationCookie']}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://{self.cookies['SsoSelectedSchool']}/student/weeklyplans/list/item/class/{week}-{year}", headers=headers)

        weeklyplan = json.loads(BeautifulSoup(resp.text, 'html.parser').find("div", {"id": "root"}).get("data-clientlogic-settings-weeklyplansapp"))
        return weeklyplan