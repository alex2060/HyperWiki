from django.shortcuts import render
from django.http import HttpResponse
import time
from django.core.files import File
from django.shortcuts import redirect

# Create your views here.


#import lets_convert
from django.shortcuts import render
#import mysql_test
import mysql.connector
import requests
import pymysql
import random
import string
import requests
#import time
import hashlib

#mysql connection function 
def try_to_connect():
    cnx = pymysql.connect(user='root', password='secret',host='mysql-server',database='app1')
    return cnx



#newkey = hashlib.sha256(passwordCandidate.encode()).hexdigest()

#makes randome string that will probaly be transfomred with hash
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str=""
    for x in range(length):
    	result_str=result_str+random.choice(letters)
    return result_str


#checks user creds
def usercheck_conect(uname,password,cnx):
	if uname=="NULL":
		return "False"
	Q1=("SELECT * FROM `a_final_users_table` WHERE `uname` LIKE \'"+uname+"\' AND `hashword` LIKE \'"+password+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q1)
	counter=0
	for row in cursor:
		counter=counter+1
	if counter!=0:
		return "True"
	return "False"

#http://localhost:8000/doit?user=u1&action_type=adduser&password=top&email=myemail
#adds user 
def add_user(uname,password,email,cnx,return_var_type):
	sql1 = "SELECT * FROM `a_final_users_table` WHERE `uname` LIKE \'"+uname+"\'";
	cursor = cnx.cursor()
	cursor.execute(sql1)
	counter=0
	for row in cursor:
		counter=counter+1
	if counter==0:
		sql="INSERT INTO `a_final_users_table` (`hashword`, `uname`, `email`,`time`) VALUES (\'"+password+"\', \'"+uname+"\', \'"+email+"]',CURRENT_TIMESTAMP);";
		cursor = cnx.cursor()
		cursor.execute(sql)
		cnx.commit()
		return "Added_user"
	return "User_in_use"


#http://localhost:8000/doit?user=u1&action_type=add_post&user=u1&password=top&text=mytest&body=mybody&photo=myphoto&catagoy=cat1&catagoy_2=cat2
#adds a post to the database and returens a post id by witch it can be foind
def add_post(uname,password,tital,text,body,photo,catagoy,catagoy_2,iframe,cnx,return_var_type):
	letsgo = usercheck_conect(uname,password,cnx)
	if letsgo=="False" or uname=="":
		return "NO_user_password"
	myrandom = get_random_string(128)
	post_id = hashlib.sha256(myrandom.encode()).hexdigest()
	sql="INSERT INTO `a_final_posts` (`uname`, `text`, `body`, `tital`, `time`, `photo`, `iframe`, `catagoy`, `catagoy_2`, `postkey`) VALUES (\'"+uname+"\', \'"+text+"\', \'"+body+"\', \'"+tital+"\', CURRENT_TIMESTAMP, \'"+photo+"\', \'"+iframe+"\', \'"+catagoy+"\', \'"+catagoy_2+"\', \'"+post_id+"\');";
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	return post_id



def add_post(key,ledgurename):
	pass

def check_priavate(key,private):
	return "True"



#http://localhost:8000/doit?action_type=get_post&user=myuser&seach1=pass&seach2=mess&catagoy=email&catagoy_2=cat2&s_type=1&usekkey=ukey&key=&seach_type=seach
#given a post id it reterns a post
def getpost(user,key,seach1,seach2,catagoy,catagoy_2,s_type,usekkey,cnx,return_var_type):
	Q1=("SELECT `uname`,`text`,`body`,`tital`,`time`,`photo`,`iframe`,`catagoy`,`catagoy_2` FROM `a_final_posts` WHERE `postkey` LIKE \'"+key+"\';")
	cursor = cnx.cursor()
	cursor.execute(Q1)
	counter=0
	out="NULL"
	private= ""
	for row in cursor:
		counter=counter+1
		out=row
		private=row[8]
	if(counter==0):
		return "no_key"
	if (check_priavate(usekkey,private)=="True"):
		return str(out[0])+" "+str(out[1])+" "+str(out[2])+" "+str(out[3])+" "+str(out[4])+" "+str(out[5])+" "+str(out[6])+" "+str(out[7])+" "+str(out[8])
	else:
		return "NO_key_private"
#http://localhost:8000/doit?user=u1&action_type=adduser&password=top&email=myemail


#http://localhost:8000/doit?user=u1&action_type=add_ledgure&password=top&email=myemail&hashword=hash&Ledgure=led
#adds a ledgure to the post
def add_ledgure(uname,password,email,hashword,Ledgure,cnx,return_var_type):
	letsgo = usercheck_conect(uname,password,cnx)
	if (letsgo==False):
		return "NO_user_password"

	sql="INSERT INTO `a_final_Ledgur` (`Ledgurename`, `Ledgurepassword`, `email`, `time`) VALUES (\'"+uname+"_"+Ledgure+"\', \'"+hashword+"\', \'"+email+"\', CURRENT_TIMESTAMP);";
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	return uname+"_"+Ledgure

#http://localhost:8000/doit?action_type=add_key&ledgure=u1_led&password=hash&message=mess&email=email&key_message=keymessage&keyfroward=keyforward
#adds a post key given creads and a ledgure
def add_key(ledgure,password,email,message,key_message,keyfroward,cnx,return_var_type):
	Q1=("SELECT `email` FROM `a_final_Ledgur` WHERE `Ledgurename` LIKE \'"+ledgure+"\' and `Ledgurepassword` LIKE \'"+password+"\';")
	cursor = cnx.cursor()
	cursor.execute(Q1)
	counter=0
	for row in cursor:
		counter=counter+1
		email_to = row[0]
	if(counter==0):
		return "NO ledgure" + Q1

	myrandom = get_random_string(128)
	post_id = hashlib.sha256(myrandom.encode()).hexdigest()

	randome2 = get_random_string(128)
	solution = hashlib.sha256(randome2.encode()).hexdigest()
	hashs = hashlib.sha256(solution.encode()).hexdigest()

	sql="INSERT INTO `a_final_Ledgur_keys` (`entery_name`, `ledgername`, `hash`, `solution`, `email`,`time`,`forward`,`key_message`) VALUES (\'"+post_id+"\', \'"+ledgure+"\', \'"+hashs+"\', 'key', \'"+email+"\', CURRENT_TIMESTAMP,\'"+keyfroward+"\',\'"+key_message+"\');";
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()

	return post_id+" "+solution+" mailto "+row[0]+" key_to "+email



#http://localhost:8000/doit?action_type=change_post&user=u1&password=top&key=&text=this
#changes a post text fild
def change_post(user,password,key,text,cnx,return_var_type):
	sql="SELECT `uname` FROM `a_final_posts` WHERE `postkey` LIKE \'"+key+"\';"
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	counter=0
	for row in cursor:
		counter=counter+1
		uname=row[0]
	if counter==0:
		return "no_post"
	letsgo = usercheck_conect(user,password,cnx)
	if user!=uname:
		return "user_named_not_matched"

	if letsgo=="False" or uname=="":
		return "NO_user_password"

	sql ="UPDATE `a_final_posts` SET `text` = \'"+text+"\' WHERE `a_final_posts`.`postkey` = \'"+key+"\'; "
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	return "text_Updated"


#http://localhost:8000/doit?action_type=change_key&user=myuser&name=&key=&newkey=this
#updata a key by solving an old one and makeing a new one and returns a keyname 
def change_key(key,name,newkey,cnx ,return_var_type):
	sql = "SELECT `hash`,`ledgername`,`forward`,`key_message` FROM `a_final_Ledgur_keys` WHERE `entery_name` LIKE \'"+name+"\' AND `solution` LIKE 'key';"
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	counter=0
	for row in cursor:
		counter=counter+1
		hashs=row[0]
		Lname=row[1]
		forward=row[1]
		key_message=row[2]
	if counter==0:
		return "NO_name"
	if hashlib.sha256(key.encode()).hexdigest()!=hashs:
		return "NO_matc"+key+" "+hashlib.sha256(key.encode()).hexdigest()+" "+hashs
	sql ="UPDATE `a_final_Ledgur_keys` SET `solution` = 'keya' WHERE `entery_name` = \'"+key+"\'; "
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()

	myrandom = get_random_string(128)
	post_id = hashlib.sha256(myrandom.encode()).hexdigest()

	sql="INSERT INTO `a_final_Ledgur_keys` (`entery_name`, `ledgername`, `hash`, `solution`, `email`,`time`,`forward`,`key_message`) VALUES (\'"+post_id+"\', \'"+Lname+"\', \'"+newkey+"\', 'key', 'none', CURRENT_TIMESTAMP,\'"+forward+"\',\'"+key_message+"\');";
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	return post_id


#http://localhost:8000/doit?action_type=check_key&name=n
#returns key inforamtiopn
def check_key(name,cnx,return_var_type):
	sql = "SELECT `hash`,`ledgername`,`solution` FROM `a_final_Ledgur_keys` WHERE `entery_name` LIKE \'"+name+"\';"
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	counter=0
	for row in cursor:
		counter=counter+1
		hashs=row[0]
		ledgername=row[1]
		sol= row[2]
	if counter==0:
		return "NO name"
	return hashs+" "+ledgername+" "+sol




#removes a key and resonrs the infomation about it.
#http://localhost:8000/doit?action_type=rm_ke&key=this&name=here
def rm_key(name,key,cnx,return_var_type):
	sql = "SELECT `hash`,`ledgername`,`forward`,`key_message`,`email` FROM `a_final_Ledgur_keys` WHERE `entery_name` LIKE \'"+name+"\' AND `solution` LIKE 'key';"
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	counter=0
	for row in cursor:
		counter=counter+1
		hashs=row[0]
		Lname=row[1]
		forward=row[1]
		key_message=row[2]
		email=row[3]
	if counter==0:
		return "NO_name_or_keytaken"
	if hashlib.sha256(key.encode()).hexdigest()!=hashs:
		return "NO_matc"+key+" "+hashlib.sha256(key.encode()).hexdigest()+" "+hashs
	sql ="UPDATE `a_final_Ledgur_keys` SET `solution` = 'remvoe' WHERE `entery_name` = \'"+name+"\'; "
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()

	myrandom = get_random_string(128)
	post_id = hashlib.sha256(myrandom.encode()).hexdigest()
	sql="INSERT INTO `a_final_posts` (`uname`, `text`, `body`, `tital`, `time`, `photo`, `iframe`, `catagoy`, `catagoy_2`, `postkey`) VALUES ('addmin', '', '', '', CURRENT_TIMESTAMP, '', '', '', \'"+Lname+"\', \'"+post_id+"\');";
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	return key_message+" "+email+" "+forward+"(???)"+key_message+"(???)"+post_id

#adds a page template and replaces some variablles


#http://localhost:8000/doit post {user,password,temmplate_name,template,template,replace}
def add_template(username,password,template_name,template,replace,cnx,return_var_type):
	letsgo = usercheck_conect(username,password,cnx)
	if replace=="":
		replace = "!"
	if letsgo=="False":
		return "NO_user_password"
	template = template.replace('\"',  '(!A???'+replace+'???A!)' )
	template = template.replace('\'',  '(!B???'+replace+'???B!)' )
	template = template.replace('`',   '(!C???'+replace+'???C!)' )
	template = template.replace('\\',  '(!D???'+replace+'???D!)' )
	try:
		sql=  "INSERT INTO `a_final_template7` (`user`, `usertemplate_name`, `template`, `time`) VALUES (\'"+username+"\', \'"+username+"_"+template_name+"\', \'"+template+"\', CURRENT_TIMESTAMP); "
		cursor = cnx.cursor()
		cursor.execute(sql)
		cnx.commit()
		return "output"
	except:
		return "dup_name"
#http://localhost:8000/doit?action_type=makepage



#sends back a tempalte returning a page after replaceing variables
#http://localhost:8000/doit?action_type=makepage&usertemplate_name=u1_mygameHSDUFNYRQSMDPNEYCQSFUYSVNMJYXT
def return_template(usertemplate_name,var1,setion,setion2,rep,cnx):
	sql = "SELECT `template` FROM `a_final_template7` WHERE `usertemplate_name` LIKE \'"+usertemplate_name+"\' "
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	counter=0
	for row in cursor:
		counter=counter+1
		template=row[0]
	if (counter==0):
		sad = sadfadsfdsf
		return "NO_template"+" "+sql
	else:
		pass
	if (rep==""):
		rep="!"
	template = template.replace('(!A???'+rep+'???A!)',  '\"' )
	template = template.replace('(!B???'+rep+'???B!)',  '\'' )
	template = template.replace('(!C???'+rep+'???C!)',   '`' )
	template = template.replace('(!D???'+rep+'???D!)',  '\\' )
	template = template.replace('(!Q???'+rep+'???Q!)',  'script' )
	template = template.replace('(!0???'+rep+'???0!)',  var1     )
	template = template.replace('(!S???'+rep+'???S!)',  setion   )
	template = template.replace('(!Z???'+rep+'???Z!)',  setion2  )
	return template




def redirect_req(var,types,cnx):
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	if types=="r":
		sql="SELECT `url` FROM `redirect` WHERE `id` LIKE 'id' "
		cursor = cnx.cursor()
		cursor.execute(sql)
		cnx.commit()
		for row in cursor:
			counter=counter+1
			url=row[0]
		return redirect(url)
	else:
		myrandom = get_random_string(128)
		post_id = hashlib.sha256(myrandom.encode()).hexdigest()
		post_id = post_id[:15]

		sql="INSERT INTO `redirect` (`id`, `url`, `time`) VALUES (\'"+post_id+"\', \'"+var+"\', CURRENT_TIMESTAMP ); "
		cursor = cnx.cursor()
		cursor.execute(sql)
		cnx.commit()
		return HttpResponse(post_id)


def print_user(req):
	return HttpResponse( "home" )
#setup up api returens and  calls other functions
def doit(req):
    #Geting input vars
    action_type=""
    try:
        action_type=req.GET["action_type"]
    except:
        action_type=""
    user=""
    try:
        user=req.GET["user"]
    except:
        user=""
    email=""
    try:
        email=req.GET["email"]
    except:
        email=""
    phone=""
    try:
        phone=req.GET["phone"]
    except:
        phone=""
    password=""
    try:
        password=req.GET["password"]
    except:
        pass
    crypto_name=""
    try:
        crypto_name=req.GET["crypto_name"]
    except:
        pass
    crypto_key=""
    try:
        crypto_key=req.GET["crypto_key"]
    except:
        pass
    crypto_path=""
    try:
        crypto_path=req.GET["crypto_path"]
    except:
        pass
    L_name=""
    try:
        L_name=req.GET["L_name"]
    except:
        pass
    request_type=""
    try:
        request_type=req.GET["request_type"]
    except:
        pass
    tital=""
    try:
        tital=req.GET["tital"]
    except:
        pass

    text=""
    try:
        text=req.GET["text"]
    except:
        pass

    body=""
    try:
        body=req.GET["body"]
    except:
        pass
    photo=""
    try:
        photo=req.GET["photo"]
    except:
        pass
    catagoy=""
    try:
        catagoy=req.GET["catagoy"]
    except:
        pass
    catagoy_2=""
    try:
        catagoy_2=req.GET["catagoy_2"]
    except:
        pass
    iframe=""
    try:
        iframe=req.GET["iframe"]
    except:
        pass
    key=""
    try:
        key=req.GET["key"]
    except:
        pass
    seach1=""
    try:
        seach1=req.GET["seach1"]
    except:
        pass
    seach2=""
    try:
        seach2=req.GET["seach2"]
    except:
        pass
    message=""
    try:
        message=req.GET["message"]
    except:
        pass

    hashword=""
    try:
        hashword=req.GET["hashword"]
    except:
        pass

    Ledgure=""
    try:
        Ledgure=req.GET["Ledgure"]
    except:
        pass

    ledgure=""
    try:
        ledgure=req.GET["ledgure"]
    except:
        pass

    name=""
    try:
        name=req.GET["name"]
    except:
        pass

    newkey=""
    try:
        newkey=req.GET["newkey"]
    except:
        pass

    seach_type=""
    try:
        seach_type=req.GET["seach_type"]
    except:
        pass

    usekkey=""
    try:
        usekkey=req.GET["usekkey"]
    except:
        pass

    key_message=""
    try:
        key_message=req.GET["keyfroward"]
    except:
        pass

    keyfroward=""
    try:
        keyfroward=req.GET["keyfroward"]
    except:
        pass
    return_var_type=""
    try:
        return_var_type=req.GET["return_var_type"]
    except:
	    pass

    if action_type=="adduser":
        if password!="":
            pass
        else:
            return HttpResponse( "Password Blank" )
        if user!="":
            pass
        else:
            return HttpResponse( "User Blank" )
        if email!="":
            pass
        else:
            return HttpResponse( "Email Blank" )
        out=add_user(user,password,email,try_to_connect())
        return HttpResponse( out )


    #Getting values
    if action_type=="add_post":
    	out = " this "
    	return  HttpResponse(add_post(user,password,tital,text,body,photo,catagoy,catagoy_2,iframe, try_to_connect(),return_var_type ) )


    if action_type=="get_post":
    	return  HttpResponse( getpost(user,key,seach1,seach2,catagoy,catagoy_2,seach_type,usekkey,try_to_connect(),return_var_type ) )

    if action_type=="add_ledgure":
    	return HttpResponse( add_ledgure(ledgure,password,email,hashword,Ledgure,try_to_connect() ,return_var_type ) )

    if action_type=="add_key":
    	return HttpResponse(  add_key(ledgure,password,email,message,key_message,keyfroward, try_to_connect() ,return_var_type ) )

    if action_type=="change_post":
    	return HttpResponse( change_post(user,password,key,text,try_to_connect() ,return_var_type ) )

    if action_type =="change_key":
    	return HttpResponse( change_key(key,name,newkey,try_to_connect(),return_var_type ) )

    if action_type =="check_key":
    	return HttpResponse( check_key(name,try_to_connect(),return_var_type ) )

    if action_type =="rm_key":
    	return HttpResponse( rm_key(name,key,try_to_connect(),return_var_type ) )

    if action_type =="red_key":
    	pass

    #templates

    mysting=action_type+","+user+","+password+","

    types=""
    user=""
    password=""
    template=""
    types=""
    replace=""
    try:
        user=req.POST["user"]
        password=req.POST["password"]
        temmplate_name=req.POST["temmplate_name"]
        template=req.POST["template"]
        types=req.POST["type"]
        replace=req.POST["replace"]
    except:
        pass
    if types!="":
        return HttpResponse(add_template(user,password,temmplate_name,template,replace,try_to_connect(),return_var_type ))
    setion=""
    try:
        setion=req.GET["setion"]
    except:
        pass
    setion2=""
    try:
        setion2=req.GET["setion2"]
    except:
        pass

    var1=""
    try:
        var1=req.GET["var1"]
    except:
	    pass
    usertemplate_name=""
    try:
        usertemplate_name=req.GET["usertemplate_name"]
    except:
        pass

    rep=""
    try:
        rep=req.GET["rep"]
    except:
	    pass
    if action_type=="makepage":
        if setion==""  or setion2=="":
            if setion=="":
                    randome2 = get_random_string(128)
                    setion = hashlib.sha256(randome2.encode()).hexdigest()
            if setion2=="":
                    randome2 = get_random_string(128)
                    setion2 = hashlib.sha256(randome2.encode()).hexdigest()
            response = redirect('http://localhost:8000/doit?action_type=makepage&usertemplate_name='+usertemplate_name+'&var1='+var1+'&rep='+rep+'&setion='+setion+'&setion2='+setion2)
            return response
        else:
            return HttpResponse(return_template(usertemplate_name,var1,setion,setion2,rep,try_to_connect() ) )

    return HttpResponse( mysting )


