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

#TODO support MOBI,HTML,AZW3 with comments[DONE] and images.

import urllib2,re,time,sys,os,optparse,urllib,locale,json,random,socket
import BeautifulSoup,yaml
TIME_OUT=200
def urlopen(url,cookiejar=None,post=None,sleepingtime=0,timeout=TIME_OUT,tring_again_times=10,
                header={
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                #"Accept-Encoding":"gzip,deflate,sdch",
                "Accept-Language":"zh-CN,zh;q=0.8",
                "Connection":"keep-alive",
                "User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
                }):
        req = urllib2.Request(url,None,header)
        opener=urllib2.build_opener() if cookiejar is None else urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        pd=urllib.urlencode(post) if post is not None else None
        time.sleep(sleepingtime)
        for _ in range(tring_again_times):
                try:
                        return opener.open(req,pd,timeout)
                except socket.timeout as e:
                        print "Failed:Time out."
                        print "Waiting for %d sec, and trying again.[%d/%d]"%(2,_+1,tring_again_times)
                        time.sleep(2)
def get_id_from_url(url):
        return re.search(ur"(\/)?(\d+)(\.html)?",url).group(2)


def chapter_page(cid,get_comments=True):
        if get_comments:
                comment_line_index_list=json.load(urlopen("http://lknovel.lightnovel.cn/main/comment_list.html",post={"chapter_id":cid}))
        def get_chapter_line_comments(lid):
                print "Getting comments @LINE-%s and waiting for about 1 sec."%lid
                #~ time.sleep(random.random()*2)
                return json.load(urlopen("http://lknovel.lightnovel.cn/main/comment_get.html",post={"chapter_id":cid,"line_id":lid}))
        def chapter_content_to_dict(content_node):
                img_node=content_node.find("img",{"class":"J_lazy J_scoll_load"})
                img= img_node.get("data-cover") if img_node is not None else None
                comments= get_chapter_line_comments(content_node.get("id")) if get_comments and content_node.get("id") in comment_line_index_list else []
                text=content_node.text.replace(u'\u3000','  ')
                return dict(img=img,text=text,comments=comments)
        soup=BeautifulSoup.BeautifulSoup(urlopen("http://lknovel.lightnovel.cn/main/view/%s.html"%cid))
        p_list=soup.findAll("div",{"class":"lk-view-line",})
        book=soup.find("h2",{"align":"center","class":"ft-32"}).text
        chapter=soup.find("h3",{"align":"center","class":"ft-20"}).text
        print "Waitting for %ds...\t@Chapter:%s"%(2,chapter)
        time.sleep(2)
        return dict(
                book=book,
                chapter=chapter,
                content=map(chapter_content_to_dict,p_list),
                )
def book_page(bid,get_comments=True):
        soup=BeautifulSoup.BeautifulSoup(urlopen("http://lknovel.lightnovel.cn/main/book/%s.html"%bid))
        chapter_list=soup.findAll("li",{"class":["span3","span3 visited"]})
        book=soup.find("h1",{"class":"ft-24"}).text
        book=re.sub("(&\w*;)","",book)
        book=re.sub("\s+"," ",book)
        print "@Book:%s"%book
        chapters=[chapter_page(re.search(ur"(view\/)(\d+)(\.html)",c.a.get("href")).group(2),get_comments=get_comments) for c in chapter_list ]
        return dict(
                book=book,
                chapters=chapters,
        )

def to_yaml(bd,path=""):
        yaml.safe_dump(bd,open(os.path.join(path,bd["book"].encode(sys.getfilesystemencoding())+".yaml"),'w'),default_flow_style=False,allow_unicode=True)
def to_txt(bd,path="",with_comments=False,encoding="UTF-8"):
        f=open(os.path.join(path,bd["book"].encode(sys.getfilesystemencoding())+".txt"),"w")
        f.write(("<< %s >>"+os.linesep*2)%(bd["book"].encode(encoding)))
        for c in bd["chapters"]:
                f.write(("< %s >"+os.linesep*2)%(c["chapter"].encode(encoding)))
                for line in c["content"]:
                        f.write(line["text"].encode(encoding))
                        f.write(os.linesep)
                        if with_comments and line["comments"]:
                                f.write("\t<comments>:"+os.linesep)
                                for cmt in line["comments"]:
                                        f.write("\t\t|:"+cmt.encode(encoding)+os.linesep)
                f.write(os.linesep+"----"+os.linesep*2)
        f.close()
def get_books_from_search(key_word,url_encoding='UTF-8'):
        url="http://lknovel.lightnovel.cn/main/booklist/%s.html"%urllib.quote(key_word.encode(url_encoding))
        soup=BeautifulSoup.BeautifulSoup(urlopen(url))
        div_list=soup.findAll("div",{"class":"lk-block"})
        return [  get_id_from_url(d.div.a.get("href")) for d in div_list]
        
        
def main():
        parse=optparse.OptionParser("[options] [book id list]")
        parse.add_option("--path","-p",default=None,help="Set output path.")
	parse.add_option("--yaml","-y",action="store_true",default=False,help="Store informations in yaml.")
	parse.add_option("--all","-a",default='',type="string",help="Search by the given keyword and download all the results.")
	parse.add_option("--comments","-c",action="store_true",default=False,help="Output with comments.")
        #TODO yaml2txt
        options,arguments=parse.parse_args()
        if not os.path.exists(options.path) and options.path:
                os.mkdir(options.path)
        #~ print repr(options.path)
        if options.all:
                ln_list=get_books_from_search(options.all.decode(locale.getpreferredencoding()))
                ln_path= options.all if options.path is '' else options.path
        else:
                ln_list=arguments
                ln_path= options.path if options.path else ''
        for i in ln_list:
                bd=book_page(re.search(ur"(\/)?(\d+)(\.html)?",i).group(2),get_comments=options.comments)
                if options.yaml:
                        to_yaml(bd,ln_path)
                to_txt(bd,options.path,with_comments=options.comments)

if __name__=='__main__':
        main()
