import httpx, time
from config import config


class XbotAuth:
    def __init__(self, xbotkey):
        self.rsp = httpx.get("https://x-bot.live/api/postman/auth?relyingParty=https%3A%2F%2Fpocket.realms.minecraft.net%2F", headers={"Authorization":xbotkey}, timeout=None).json()
        self.uhs: str = self.rsp['userHash']
        self.xsts: str = self.rsp['XSTSToken']
        self.xbl3: str = f"XBL3.0 x={self.uhs};{self.xsts}"

    def token(self):
        return self.xbl3
        
    def realm_headers(self):
        return {
            'Cache-Control': 'no-cache',
            'Charset': 'utf-8',
            'Client-Version': '1.19.20',
            'User-Agent': 'MCPE/UWP',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'pocket.realms.minecraft.net',
            'Authorization': self.xbl3
        }


class RealmAPI:
    def __init__(self, auth: XbotAuth):
        self.auth = auth
        self.worlds = self.get_worlds()

    def get_worlds(self):
        rsp = httpx.get("https://pocket.realms.minecraft.net/worlds", headers=self.auth.realm_headers())
        self.worlds = [each['id'] for each in rsp.json()['servers']]
        return self.worlds

    def get_world_players(self, world_id):
        if world_id not in self.get_worlds():
            return "Sorry, the currently authenticated account does not own the specified world"
        rsp = httpx.get(f"https://pocket.realms.minecraft.net/worlds/{world_id}", headers=self.auth.realm_headers())
        if "players" in rsp.json().keys():
            return [each["uuid"] for each in rsp.json()["players"]]
        else:
            return []


if __name__ == "__main__":
    auth = XbotAuth(config["XBOTKEY"])
    realm = RealmAPI(auth)
    realm.get_worlds()
    worlds = realm.worlds
    for each in worlds:
        print(f"Debug: checking world {each}")
        plrs = realm.get_world_players(each)
        if len(plrs):
            print(f"World {each} has {len(plrs)} players:\n  {plrs}")
        time.sleep(2)