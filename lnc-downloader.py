#!/usr/bin/env python
#encoding=UTF-8
#  
#  Copyright 2014 MopperWhite <mopperwhite@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import urllib2,re,time,sys,os,optparse
import BeautifulSoup,yaml
TIME_OUT=20
def urlopen(url,cookiejar=None):
        header={
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        #"Accept-Encoding":"gzip,deflate,sdch",
        "Accept-Language":"zh-CN,zh;q=0.8",
        "Connection":"keep-alive",
        "User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
        }
        req = urllib2.Request(url,None,header)
        if cookiejar is None:
                opener=urllib2.build_opener()
        else:
                opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        return opener.open(req,None,TIME_OUT)

def chapter_page(cid):
        soup=BeautifulSoup.BeautifulSoup(urlopen("http://lknovel.lightnovel.cn/main/view/%s.html"%cid))
        p_list=soup.findAll("div",{"class":"lk-view-line"})
        book=soup.find("h2",{"align":"center","class":"ft-32"}).text
        chapter=soup.find("h3",{"align":"center","class":"ft-20"}).text
        print "Waitting...%ds\t@Chapter:%s"%(2,chapter)
        time.sleep(2)
        return dict(
                book=book,
                chapter=chapter,
                context=[p.text.replace(u'\u3000',' ') for p in p_list],
                )
def book_page(bid):
        soup=BeautifulSoup.BeautifulSoup(urlopen("http://lknovel.lightnovel.cn/main/book/%s.html"%bid))
        chapter_list=soup.findAll("li",{"class":"span3"})
        book=soup.find("h1",{"class":"ft-24"}).text
        book=re.sub("(&\w*;)","",book)
        book=re.sub("\s+"," ",book)
        print "@Book:%s"%book
        chapters=[chapter_page(re.search(ur"view\/(\d+)\.html",c.a.get("href")).group(1)) for c in chapter_list ]
        return dict(
                book=book,
                chapters=chapters,
        )

def to_yaml(bd,path=""):
        yaml.safe_dump(bd,open(os.path.join(path,bd["book"].encode(sys.getfilesystemencoding())+".yaml"),'w'),default_flow_style=False,allow_unicode=True)
def to_txt(bd,path="",encoding="UTF-8"):
        f=open(os.path.join(path,bd["book"].encode(sys.getfilesystemencoding())+".txt"),"w")
        f.write(("<< %s >>"+os.linesep*2)%(bd["book"].encode(encoding)))
        for c in bd["chapters"]:
                f.write(("< %s >"+os.linesep*2)%(c["chapter"].encode(encoding)))
                f.write((os.linesep).join(c["context"]).encode(encoding))
                f.write(os.linesep+"----"+os.linesep*2)
        f.close()
def main():
        parse=optparse.OptionParser()
        parse.add_option("--path","-p",default="")
	parse.add_option("--yaml","-y",action="store_true")
        options,arguments=parse.parse_args()
        if not os.path.exists(options.path) and options.path is not '':
                os.mkdir(options.path)
        print repr(options.yaml)
        for i in arguments:
                bd=book_page(re.search(ur"(\/)?(\d+)(\.html)?",i).group(2))
                if options.yaml:
                        to_yaml(bd,options.path)
                to_txt(bd,options.path)

if __name__=='__main__':
        main()
