#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import argparse
import os
import glob

import time
import MeCab

import urllib3
#import urllib.request, urllib.error
from bs4 import BeautifulSoup


def url_open(url):
  http = urllib3.PoolManager()
  r = http.request('GET',url)
  #print(r.data)
  #print(r.status)
  
  #html = urllib3.urlopen(url)
  soup = BeautifulSoup(r.data,"lxml")

  return soup
  
def html2link(soup,filename):
  #atag = soup.find_all("a")
  #print(atag)
  #f1 = open(filename,"w")
  num = 0
  http = urllib3.PoolManager()
  link = []
  for line in soup.find_all("a"):


    htag = line.get("href")
    if "/rb/" in str(htag):
      print(htag)
      link.append(htag)

  print(link)
  l = []
  link2 = list(set(link))
  print(link2)
  
  for l in link2:
    if num > 20:
      break    
    f1 = open(filename,"a")
    num += 1
    print(l)
    http = urllib3.PoolManager()
    r = http.request('GET',l)
    soup = BeautifulSoup(r.data,"lxml")
    print("書き込み")
    f1.write("num:::::" + str(num) + "\n")
    f1.write("url:::::" + l + "\n")
    f1.write(str(soup) + "\n")
    time.sleep(2)

def link2rec(filename,soup):
  f2 = open(filename)
  lines = f2.readlines()
  c = 5
  sentence = {}
  for line in lines:
    if "url:::::" in line:
      l = line.replace("url:::::","")
      l = line.replace("\n","")
      url = l
    elif "<h2>商品説明" in line:
      c = 0
    elif "<p>" in line:
      c = c
    else:
      c += 1
    if c == 2:
      sen = line
      sentence[url] = sen
  sp = []
  
  sp = str(soup).split("\n")
  c = 5
  for l in sp:
    if "<h2>商品説明" in l:
      c = 0
    elif "<p>" in l:
      c = c
    else:
      c += 1
    if c == 2:
      sentence["master"] = l

  return sentence

def jaccard(list_a,list_b):
  set_intersection = set.intersection(set(list_a), set(list_b))
  num_intersection = len(set_intersection)
  
  set_union = set.union(set(list_a), set(list_b))
  num_union = len(set_union)
  return float(num_intersection) / num_union

def calc_jaccard(sentence):
  mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
  mecab.parse('')
  word_d = {}
  for u,s in sentence.items():
    node = mecab.parseToNode(s)
    wordlist = []
    while node:
      if node.feature.split(",")[6] == '*':
        word = node.surface
      else:
        word = node.feature.split(",")[6]      

      part = node.feature.split(",")[0]

      if part in ["名詞", "形容詞", "動詞"] and word != "BR":
        wordlist.append(word)
      node = node.next
    #print(wordlist)

    word_d[u] = wordlist
  master = word_d["master"]
  j1 = 0
  j2 = 0
  j3 = 0
  for u,w in word_d.items():
    if not u == "master":
      u = u.replace("url:::::","")
      j = jaccard(master,w)
      if j1 < j:
        j1 = j
        j1_url = u
      elif j2 < j:
        j2 = j
        j2_url = u
      elif j3 < j:
        j3 = j
        j3_url = u
  return j1_url, j2_url, j3_url



  return word_d
#def target()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input_url', action='store', nargs='?', type=str)
  parser.add_argument('-o', '--output_dir', action='store', nargs='?', type=str)
  args = parser.parse_args()
  url = args.input_url
  output = args.output_dir
  print("https://books.rakuten.co.jp/rb/で始まるURLを入力してください。")
  url = input()
  urlsp = []
  urlsp = url.split("/")
  pnum = urlsp[-2]
  #print(pnum)
  output = output + pnum + ".txt"
  #print(url)
  if os.path.isfile(output) == False:

    soup =  url_open(url)
    html2link(soup,output)
  
    f_soup = open(output+ ".input","w")
    f_soup.write(str(soup))

  f_s = open(output+ ".input")
  soup = f_s.read()
  rec = link2rec(output,soup)
  
  #print(rec["master"])
  u1,u2,u3 = calc_jaccard(rec)
  print("結果は以下の通りです。")
  print(u1)
  print(u2)
  print(u3)
  
  #print(rec)
