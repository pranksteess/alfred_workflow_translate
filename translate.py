from workflow import Workflow3
import googletrans
import deepl
import os
import sys
import json
import random
import hashlib
import time
import requests

def use_youdao(msg, lang):
	if lang == "ZH":
		lang == "ZH-CHS"
	lang = str.lower(lang)

	def truncate(q):
		if q is None:
			return None
		size = len(q)
		return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]

	appid = os.getenv("youdao_appid")
	sec = os.getenv("youdao_sec")
	appid = "2dbf3a58df74d70b"
	sec = "LQ4lEgCqLiK5IVa0yqsQ4al6KUjRGooJ"
	curr_time = str(int(time.time()))
	salt = str(random.randint(32768, 65536))
	sign = appid + truncate(msg) + salt + curr_time + sec
	sign = hashlib.sha256(sign.encode()).hexdigest()

	url = 'https://openapi.youdao.com/api'

	params = {
		"q": msg,
		"from": "auto",
		"to": lang,
		"appKey": appid,
		"salt": salt,
		"curtime": curr_time,
		"sign": sign,
		"signType": "v3"
	}

	response = requests.get(url, params=params)
	result = response.json()
	return result.get("translation")[0]


def use_deepl(msg, lang):
	auth_key = os.getenv("deepl_api_key")
	translator = deepl.Translator(auth_key)
	result = translator.translate_text(msg, target_lang=lang)
	return result.text

def use_google(msg, lang):
	if lang == "ZH":
		lang = "ZH-CN"
	elif lang == "EN-US":
		lang = "EN"
	lang = str.lower(lang)
	translator = googletrans.Translator()
	result = translator.translate(msg, lang)
	return result.text

def translate(msg, lang):
	r0 = use_deepl(msg, lang)
	r1 = use_google(msg, lang)
	r2 = use_youdao(msg, lang)
	return [("Deepl", r0), ("Google", r1), ("YouDao", r2)]

def main(wf):
	image_path = "./assets/images/"
	msg = ' '.join(sys.argv[1:])
	source_lang = googletrans.Translator().detect(msg).lang
	target_lang = os.getenv("target_lang")
	if str.upper(source_lang[:2]) == str.upper(target_lang[:2]):
		if target_lang == "EN":
			target_lang = "ZH"
		else:
			target_lang = "EN-US"

	
	res_list  = translate(msg, target_lang)
	for r in res_list:
		wf.add_item(r[1], r[0]+" Translate", r[1], icon=image_path+r[0]+".png", valid=True)

	wf.send_feedback()

if __name__ == '__main__':
	wf = Workflow3()
	log = wf.logger
	sys.exit(wf.run(main))
