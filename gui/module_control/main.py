# -*- coding: utf-8 -*-

from requests import Session, exceptions
from bs4 import BeautifulSoup as bs

with Session() as s:
<<<<<<< HEAD
    site = s.get(r"http://192.168.1.78/login", timeout=2)
=======
    site = s.get(r"http://192.168.1.78/login")
>>>>>>> origin/main

    bs_content = bs(site.content, "html.parser")
    token = bs_content.find("input", {"name": "__PPAS"})

    # login
    state = s.post(r"http://192.168.1.78/state", data={'__PPAS': 'admin'})
    print(state.content.decode('gb2312'))

    state = home_page = s.post(r"http://192.168.1.78/uart")
    print(state.content.decode('gb2312'))
