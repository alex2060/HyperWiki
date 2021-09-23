from django.shortcuts import render
from django.http import HttpResponse
import time
from django.core.files import File
from django.shortcuts import redirect
from django.shortcuts import render
import mysql.connector
import requests
import pymysql
import random
import string
import requests
import hashlib
import json
import braintree
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
def try_to_connect():
    cnx = pymysql.connect(user='root', password='secret',host='mysql-server',database='app1')
    return cnx

#home page
def print_user(req):
    f = open("home.html", "r")
    out= f.read()
    f.close()

    return HttpResponse( out )

#payment gateway for items and keys
def payment_gateway(req):
    gateway = braintree.BraintreeGateway(
	    braintree.Configuration(
	        environment=braintree.Environment.Sandbox,
	        merchant_id="x7h65pb7jq88w5qw",
	        public_key="5pw64887tvj3qjym",
	        private_key="500e0113aac551b7715d01cbc218c0f0",
	    )
    )
    client_token=gateway.client_token.generate()
    f = open("new.html", "r")
    out= f.read()
    f.close()
    item = "";
    try:
        item=req.GET["item"]
    except:
        pass
    cnx = try_to_connect()
    sql= "SELECT `path`,`url` FROM `items` WHERE `itemname` LIKE \'"+item+"\';"
        
    cursor = cnx.cursor()
    cursor.execute(sql)
    counter=0
    for row in cursor:
        counter=counter+1
        amount  = row[0]
    if counter==0:
        return HttpResponse("noitem")
    out = out.replace('(!C???C!)',  client_token )
    out = out.replace('(!A???A!)',  amount )
    out = out.replace('(!I???I!)',  item )
    cnx = try_to_connect()


    return HttpResponse(out)

#payment retun
def create_checkout(request):
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
        environment=braintree.Environment.Sandbox,
        merchant_id="x7h65pb7jq88w5qw",
        public_key="5pw64887tvj3qjym",
        private_key="500e0113aac551b7715d01cbc218c0f0",
        )
    )
    result = gateway.transaction.sale({
        'amount': request.POST['amount'],
        'payment_method_nonce': request.POST['payment_method_nonce'],
        'options': {
        "submit_for_settlement": True
        }
    })
    if result.is_success or result.transaction:
        print("in here")
        TRANSACTION_SUCCESS_STATUSES = [
   			braintree.Transaction.Status.Authorized,
    		braintree.Transaction.Status.Authorizing,
    		braintree.Transaction.Status.Settled,
   			braintree.Transaction.Status.SettlementConfirmed,
    		braintree.Transaction.Status.SettlementPending,
    		braintree.Transaction.Status.Settling,
    		braintree.Transaction.Status.SubmittedForSettlement
        ]
        print(request.POST['amount'])
        val = gateway.transaction.find(result.transaction.id)
        lastcheck = val.status in TRANSACTION_SUCCESS_STATUSES
        item = "";
        cnx = try_to_connect()
        sql = "SELECT `url` FROM `items` WHERE `itemname` LIKE \'"+request.POST['Item']+"\' AND `path` LIKE \'"+request.POST['amount']+"\'"
        cursor = cnx.cursor()
        cursor.execute(sql)
        counter=0
        myvalue=""
        for row in cursor:
            counter=counter+1
            url  = row[0]
            x = requests.get(url)
            myvalue = x.content.decode('utf-8')
        f = open("done.html", "r")
        out= f.read()
        f.close()
        if result.is_success:
            out = out.replace('(!I???I!)',  str(myvalue) )
            return HttpResponse( out )
        else:
        	return HttpResponse("Failed to prossess")
    else:
    	return HttpResponse("Failed to prossess")

#gets randome sting of chars to be hashed
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str=""
    for x in range(length):
    	result_str=result_str+random.choice(letters)
    return result_str

#not called by user
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

#Adds user to database
def add_user(uname,password,email,cnx,return_var_type):
	sql1 = "SELECT * FROM `a_final_users_table` WHERE `uname` LIKE \'"+uname+"\'";
	cursor = cnx.cursor()
	cursor.execute(sql1)
	counter=0
	for row in cursor:
		counter=counter+1
	#adds fame money to there acount
	if counter==0:
		sql="INSERT INTO `a_final_users_table` (`hashword`, `uname`, `email`,`time`) VALUES (\'"+password+"\', \'"+uname+"\', \'"+email+"]',CURRENT_TIMESTAMP);";
		cursor = cnx.cursor()
		cursor.execute(sql)
		cnx.commit()
		dictionary ={ 
		  "response": "ADDED_USER"
		} 
		query = ("INSERT INTO `job_usertable` (`username`, `password`, `creation`, `email`) VALUES (\'"+uname+"\', \'"+password+"\', CURRENT_TIMESTAMP, \'"+email+"\');")
		#print(query)
		cursor = cnx.cursor()
		cursor.execute(query)
		cnx.commit()
		#adds money to user
		query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+uname+"\', \'"+uname+"_money1\', 'money1', '1000');")
		cursor = cnx.cursor()
		cursor.execute(query2)
		cnx.commit()
		#adds money to user
		query3=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+uname+"\', \'"+uname+"_money2\', 'money2', '1000');")
		cursor = cnx.cursor()
		cursor.execute(query3)
		cnx.commit()
		cnx.close()

		return json.dumps(dictionary, indent = 4)

	dictionary ={ 
	  "response": "USER_TAKEN"
	} 
	return json.dumps(dictionary, indent = 4)

#adds a post to the database and returens a post id by witch it can be foind
def add_post(uname,password,tital,text,body,photo,catagoy,catagoy_2,iframe,cnx,return_var_type):
	letsgo = usercheck_conect(uname,password,cnx)
	if letsgo!="True" and uname!="":
		dictionary ={ 
		  "id": "NA "+uname+" "+password+" "+letsgo
		} 
		return json.dumps(dictionary, indent = 4)
	myrandom = get_random_string(128)
	post_id = hashlib.sha256(myrandom.encode()).hexdigest()
	sql="INSERT INTO `a_final_posts` (`uname`, `text`, `body`, `tital`, `time`, `photo`, `iframe`, `catagoy`, `catagoy_2`, `postkey`) VALUES (\'"+uname+"\', \'"+text+"\', \'"+body+"\', \'"+tital+"\', CURRENT_TIMESTAMP, \'"+photo+"\', \'"+iframe+"\', \'"+catagoy+"\', \'"+catagoy_2+"\', \'"+post_id+"\');";
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	dictionary ={ 
	  "id": post_id
	} 
	return json.dumps(dictionary, indent = 4)

#checks to see if a post is private
def check_priavate(key,private,cnx):
	if private=="":
		return "True"
	sql="SELECT * FROM `a_final_posts` WHERE `uname` LIKE 'addmin' AND `catagoy_2` LIKE \'"+private+"\' AND `postkey` LIKE \'"+key+"\';"
	cursor = cnx.cursor()
	cursor.execute(sql)
	counter=0
	for row in cursor:
		counter=counter+1
	if (counter==1):
		return "True"
	return "False"

#Given a post id it reterns a post
def getpost(key,usekkey,cnx,return_var_type):
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
		dictionary ={ 
		  "id": "post_is_NA",
		  "username": str("NA"),
		  "text": str("NA"),
		  "body": str("NA"),
		  "tital": str("NA"),
		  "time" : str("NA"),
		  "photo": str("NA"),
		  "iframe": str("NA"),
		  "catagoy": str("NA"),
		  "catagoy_2": str("NA")

		} 
		return json.dumps(dictionary, indent = 4)
	if (check_priavate(usekkey,private,cnx)=="True"):
		dictionary ={ 
		  "id": key,
		  "username": str(out[0]),
		  "text": str(out[1]),
		  "body": str(out[2]),
		  "tital": str(out[3]),
		  "time" : str(out[4]),
		  "photo": str(out[5]),
		  "iframe": str(out[6]),
		  "catagoy": str(out[7]),
		  "catagoy_2": str(out[8])

		} 
		return json.dumps(dictionary, indent = 4)
	else:
		dictionary ={ 
		  "id": "post_is_private+"+private,
		  "username": str("NA"),
		  "text": str("NA"),
		  "body": str("NA"),
		  "tital": str("NA"),
		  "time" : str("NA"),
		  "photo": str("NA"),
		  "iframe": str("NA"),
		  "catagoy": str("NA"),
		  "catagoy_2": str("NA")

		} 
		return json.dumps(dictionary, indent = 4)

#adds a ledgure to the post
def add_ledgure(uname,password,email,hashword,Ledgure,cnx,return_var_type):
	letsgo = usercheck_conect(uname,password,cnx)
	if (letsgo==False or uname==""):
		dictionary ={ 
		  "output": "user_taken",
		} 
		return json.dumps(dictionary, indent = 5)
	try:
		sql="INSERT INTO `a_final_Ledgur` (`Ledgurename`, `Ledgurepassword`, `email`, `time`) VALUES (\'"+uname+"_"+Ledgure+"\', \'"+hashword+"\', \'"+email+"\', CURRENT_TIMESTAMP);";
		cursor = cnx.cursor()
		cursor.execute(sql)
		cnx.commit()
		dictionary ={ 
		  "output": "added "+uname+"_"+Ledgure,
		} 
		return json.dumps(dictionary, indent = 5)
	except:
		dictionary ={ 
		  "output": "taken",
		}
		return json.dumps(dictionary, indent = 5)
	return uname+"_"+Ledgure

#adds a Post key given creads and a ledgure
def add_key(ledgure,password,email,message,key_message,keyfroward,cnx,return_var_type):
	path = "http://localhost:8000/doit?"
	Q1=("SELECT `email` FROM `a_final_Ledgur` WHERE `Ledgurename` LIKE \'"+ledgure+"\' and `Ledgurepassword` LIKE \'"+password+"\';")
	cursor = cnx.cursor()
	cursor.execute(Q1)
	counter=0
	for row in cursor:
		counter=counter+1
		email_to = row[0]
	#case no leddudurename_password
	if(counter==0):
		dictionary ={ 
		  "post_id": "NA",
		  "solution": "NA",
		  "SQL":Q1
		}
		return json.dumps(dictionary, indent = 5)
	myrandom = get_random_string(128)
	post_id = hashlib.sha256(myrandom.encode()).hexdigest()
	randome2 = get_random_string(128)
	solution = hashlib.sha256(randome2.encode()).hexdigest()
	hashs = hashlib.sha256(solution.encode()).hexdigest()
	sql="INSERT INTO `a_final_Ledgur_keys` (`entery_name`, `ledgername`, `hash`, `solution`, `email`,`time`,`forward`,`key_message`) VALUES (\'"+post_id+"\', \'"+ledgure+"\', \'"+hashs+"\', 'key', \'"+email+"\', CURRENT_TIMESTAMP,\'"+keyfroward+"\',\'"+key_message+"\');";
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	#removes key
	dictionary ={ 
	  "post_id": post_id,
	  "solution": solution,
	  "email":email,
	  "message":key_message,
	  "ledgure_ownder_email":email_to,
	  "land_url":path+"action_type=makepage&usertemplate_name=u1_mygameSEHTRJFCNLVXNRNSFVJXITPCKPKBPH&var1="+post_id+"?"+solution,
	  "ledgure": ledgure,
	  "path":path
	}
	#where add key funtion would go
	return json.dumps(dictionary, indent = 5)

#changes a post text fild OF post
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
		dictionary ={ 
		  "output": "NO_Post_Found"+" "+sql,
		}
		return json.dumps(dictionary, indent = 5)
	letsgo = usercheck_conect(user,password,cnx)
	if user!=uname:
		return "user_named_not_matched"
	if user=="":
		letsgo="True"
	if letsgo=="False":
		dictionary ={ 
		  "output": "NO_user_password",
		}
		return json.dumps(dictionary, indent = 5)
	sql ="UPDATE `a_final_posts` SET `text` = \'"+text+"\' WHERE `a_final_posts`.`postkey` = \'"+key+"\'; "
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	dictionary ={ 
	  "output": "text_updated",
	}
	return json.dumps(dictionary, indent = 5)

#update a key by solving an old one and makeing a new one and returns a keyname 
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
		dictionary ={ 
		  "output": "NO_name_or_key_taken",
		}
		return json.dumps(dictionary, indent = 5)

	if hashlib.sha256(key.encode()).hexdigest()!=hashs:
		dictionary ={ 
		  "output": "NO_match"+key+" "+hashlib.sha256(key.encode()).hexdigest()+" "+hashs
		}
		return json.dumps(dictionary, indent = 5)
	#change key case
	sql ="UPDATE `a_final_Ledgur_keys` SET `solution` = \'"+key+"\' WHERE `entery_name` = \'"+name+"\'; "
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()

	myrandom = get_random_string(128)
	post_id = hashlib.sha256(myrandom.encode()).hexdigest()
	sql="INSERT INTO `a_final_Ledgur_keys` (`entery_name`, `ledgername`, `hash`, `solution`, `email`,`time`,`forward`,`key_message`) VALUES (\'"+post_id+"\', \'"+Lname+"\', \'"+newkey+"\', 'key', 'none', CURRENT_TIMESTAMP,\'"+forward+"\',\'"+key_message+"\');";
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	dictionary ={ 
	  "output": post_id,
	}
	return json.dumps(dictionary, indent = 5)

#returns key inforamtiopn
def check_key(name,cnx,return_var_type):
	sql = "SELECT `hash`,`ledgername`,`solution` FROM `a_final_Ledgur_keys` WHERE `entery_name` LIKE \'"+name+"\';"
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	counter=0
	for row in cursor:
		counter    =counter+1
		hashs      =row[0]
		ledgername =row[1]
		sol        =row[2]
	if counter==0:
		dictionary ={ 
		  "output": "NA",
		  "hash":"NA",
		  "ledgure":"NA",
		  "solution":"NA"
		}
		return json.dumps(dictionary, indent = 5)
	dictionary ={ 
	  "output": name,
	  "hash":hashs,
	  "ledgure":ledgername,
	  "solution":sol
	}
	return json.dumps(dictionary, indent = 5)

#removes a key and resonrs the infomation about it. can also froward infromation
def rm_key(name,key,message,cnx,return_var_type):
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
	#a =sdfadsf
	if counter==0:
		dictionary ={ 
		  "key_message": "NA",
		  "email":"NA",
		  "forward":"NA",
		  "key_message":"NA",
		  "post_id":"NO_Key"
		}
		return json.dumps(dictionary, indent = 5)
	if hashlib.sha256(key.encode()).hexdigest()!=hashs:
		dictionary ={ 
		  "key_message": "NA",
		  "email":"NA",
		  "forward":"NA",
		  "key_message":"NA",
		  "post_id":"NO_match"
		}
		return json.dumps(dictionary, indent = 5)
	#removing key and sending back_info_to_user
	sql ="UPDATE `a_final_Ledgur_keys` SET `solution` = \'"+key+"\' WHERE `entery_name` = \'"+name+"\'; "
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	myrandom = get_random_string(128)
	post_id = hashlib.sha256(myrandom.encode()).hexdigest()
	sql="INSERT INTO `a_final_posts` (`uname`, `text`, `body`, `tital`, `time`, `photo`, `iframe`, `catagoy`, `catagoy_2`, `postkey`) VALUES ('addmin', '', '', '', CURRENT_TIMESTAMP, '', '', '', \'"+Lname+"\', \'"+post_id+"\');";
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	dictionary ={ 
	  "key_message": str(key_message),
	  "email":str(hashs),
	  "forward":str(forward),
	  "key_message":str(key_message),
	  "post_id":str(post_id),
	  "ledgure":str(Lname),
	  "mesage_to_send":str(message)
	}
	#where send logic is handeled

	return json.dumps(dictionary, indent = 5)

#adds a template with post see posturl.html for an example as this uses post makes a html template to be used by user
def add_template(username,password,template_name,template,replace,cnx,return_var_type):
	letsgo = usercheck_conect(username,password,cnx)
	if replace=="":
		replace = "!"
	if letsgo=="False":
		dictionary ={ 
		  "output": "NO_user_password"
		}
		return json.dumps(dictionary, indent = 4)
	#repalceing template wiht strings
	template = template.replace('\"',  '(!A???'+replace+'???A!)' )
	template = template.replace('\'',  '(!B???'+replace+'???B!)' )
	template = template.replace('`',   '(!C???'+replace+'???C!)' )
	template = template.replace('\\',  '(!D???'+replace+'???D!)' )
	try:
		sql=  "INSERT INTO `a_final_template7` (`user`, `usertemplate_name`, `template`, `time`) VALUES (\'"+username+"\', \'"+username+"_"+template_name+"\', \'"+template+"\', CURRENT_TIMESTAMP); "
		cursor = cnx.cursor()
		cursor.execute(sql)
		cnx.commit()
		dictionary ={ 
		  "output": "added_tempalte "+username+"_"+template_name 
		}
		return json.dumps(dictionary, indent = 4)
	except:
		#case name taken
		dictionary ={ 
		  "output": "dup_name"
		}
		return json.dumps(dictionary, indent = 4)

#Sends back a tempalte returning a page after replaceing variables makes a setion post with a given id not called by user
def make_setion(myid,cnx):
	sql="INSERT INTO `a_final_posts` (`uname`, `text`, `body`, `tital`, `time`, `photo`, `iframe`, `catagoy`, `catagoy_2`, `postkey`) VALUES ('', '', '', '', CURRENT_TIMESTAMP, '', '', '', '', \'"+myid+"\');";
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()

#returns a template 
def return_template(usertemplate_name,var1,setion,setion2,rep,cnx):
	path="http://localhost:8000/doit"
	sql = "SELECT `template` FROM `a_final_template7` WHERE `usertemplate_name` LIKE \'"+usertemplate_name+"\' "
	cursor = cnx.cursor()
	cursor.execute(sql)
	cnx.commit()
	counter=0
	for row in cursor:
		counter=counter+1
		template=row[0]
	if (counter==0):
		#case no template
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
	template = template.replace('(!P???'+rep+'???P!)',  path  )
	template = template.replace('(!T???'+rep+'???T!)',  usertemplate_name  )
	return template

#makes and redirects urls
def redirect_req(var,types,cnx):
	if types=="r":
		sql="SELECT `url` FROM `redirect` WHERE `id` LIKE \'"+var+"\' "
		cursor = cnx.cursor()
		cursor.execute(sql)
		cnx.commit()
		counter=0
		for row in cursor:
			counter=counter+1
			url=row[0]
		if counter==0:
			dictionary ={ 
			  "id": "NOURL"
			} 
			return HttpResponse(json.dumps(dictionary, indent = 4))
		return redirect(url)
	else:
		myrandom = get_random_string(128)
		post_id = hashlib.sha256(myrandom.encode()).hexdigest()
		post_id = post_id[:15]
		sql="INSERT INTO `redirect` (`id`, `url`, `time`) VALUES (\'"+post_id+"\', \'"+var+"\', CURRENT_TIMESTAMP ); "
		cursor = cnx.cursor()
		cursor.execute(sql)
		cnx.commit()
		dictionary ={ 
		  "id": post_id
		} 

#calls url page
def under_call(url):
	try:
		x = requests.get(url)
		return x.content
	except:
		return "NONE"

#finishes traid via traid id
def funtion_make_traid(username, password ,traid_money_type,traid_money_amount,request_money_type,request_amount ,cnx):
	try:
		float(request_amount)
		float(traid_money_amount)
	except:
		dictionary ={ 
		  "response": "Invaild",
		  "amnountleft":"NA"
		} 
		return json.dumps(dictionary, indent = 4)

	if username=="NULL":
		dictionary ={ 
		  "response": "Wrong_Username",
		  "amnountleft":"NA"
		} 
		return json.dumps(dictionary, indent = 4)
	is_user=usercheck_conect(username,password,cnx)
	if is_user=="False":
		dictionary ={ 
		  "response": "Wrong_Username",
		  "amnountleft":"NA"
		} 
		return json.dumps(dictionary, indent = 4)
	traidid=get_random_string(64)
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+username+"_"+traid_money_type+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		money=row[0]
	amnountleft=money-traid_money_amount
	if amnountleft>0:
		pass
	else:
		#case no funds in user acount
		dictionary ={ 
		  "response": "No_Funds",
		  "amnountleft":"NA"
		} 
		return json.dumps(dictionary, indent = 4)
	#event where there are user funds in acount
	U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+username+"_"+traid_money_type+"';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()
	Q1=("INSERT INTO `traidtable` (`traid_id`, `traid_mony_type`, `traid_request_type`, `traid_request_amount`, `traid_money_amount`, `user`, `buyer`) VALUES (\'"+traidid+"\', \'"+traid_money_type+"\', \'"+request_money_type+"\', \'"+str(request_amount)+"\', \'"+str(traid_money_amount)+"\', \'"+username+"\', 'NULL');")
	cursor = cnx.cursor()
	cursor.execute(Q1)
	cnx.commit()
	counter=0
	cnx.close()
	dictionary ={ 
	  "response": traidid,
	  "amnountleft":str(amnountleft)
	} 
	return json.dumps(dictionary, indent = 4)

#compleate traid with traid id
def compleat_traid_comand(user,password,traid_id,cnx):
	if user=="NULL":
		dictionary ={ 
		  "response": "NO_USER",
		}
		return json.dumps(dictionary, indent = 4)
	is_user=usercheck_conect(user,password,cnx)
	if is_user=="False":
		dictionary ={ 
		  "response": "NO_USER",
		}
		return json.dumps(dictionary, indent = 4)
	sql=("SELECT `traid_mony_type`,`traid_request_type`,`traid_request_amount`,`traid_money_amount`,`buyer`,`user` FROM `traidtable` WHERE `traid_id` LIKE \'"+traid_id+"\' AND `buyer` LIKE 'NULL';")
	cursor = cnx.cursor()
	cursor.execute(sql)
	counter=0
	for row in cursor:
		counter=1
		traid_mony_type=row[0]
		traid_request_type=row[1]
		traid_request_amount=row[2]
		traid_money_amount=row[3]
		buyer=row[4]
		reciver=row[5]
	#substack form payied user
	if counter==0:
		dictionary ={ 
		  "response": "No_Traid",
		}
		return json.dumps(dictionary, indent = 4)
	#verifies theres enough money user acount
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+user+"_"+traid_request_type+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		money=row[0]
	amnountleft=money-traid_request_amount
	if amnountleft>0:
		pass
	else:
		dictionary ={ 
		  "response": "No_Funds",
		}
		return json.dumps(dictionary, indent = 4)
	U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+user+"_"+traid_request_type+"';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()

	#put money gained form train to taker of traid
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+reciver+"_"+traid_request_type+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		money=row[0]
	amnountleft=money+traid_request_amount
	U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+reciver+"_"+traid_request_type+"';")
	cursor = cnx.cursor()
	cursor.execute(U1)

	#add to user acount who made traid
	checkandadd_money_type(user,traid_mony_type,cnx)
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+user+"_"+traid_mony_type+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		money=row[0]
	amnountleft=money+traid_money_amount

	#add money to user acount
	U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+user+"_"+traid_mony_type+"';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()
	#update buyer
	Q0=("UPDATE `traidtable` SET `buyer` = \'"+user+"\' WHERE `traidtable`.`traid_id` = \'"+traid_id+"\';")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	cnx.commit()
	cnx.close()
	#print(traid_mony_type,traid_request_type,traid_request_amount,traid_money_amount,buyer,reciver)
	dictionary ={ 
	  "response": traid_id,
	}
	return json.dumps(dictionary, indent = 4)
	return traid_id;

#add barter curancy to acount
def get_key2(path,ledgure_name,keyname,password):
	#get barter key
	myurl = path+"?action_type=check_key&name="+keyname
	x = requests.get(myurl)
	getarray = json.loads(x.content.decode('utf-8'))
	if getarray["hash"]!="NA":
		print("passed_leddgure")
	else:
		return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	if getarray["ledgure"]==ledgure_name:
		print("passed_leddgure")
	else:
		return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	passwordCandidate = password
	val = hashlib.sha256(passwordCandidate.encode()).hexdigest()
	if val==getarray["hash"]:
		print("passed_key")
	else:
		return [False,"Failed_key",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	random_string=""
	#generate and sores new crypto
	for _ in range(100):
	    random_integer = random.randint(65, 80)
	    random_string += (chr(random_integer))
	passwordCandidate = random_string
	newkey = hashlib.sha256(passwordCandidate.encode()).hexdigest()
	keyhash = hashlib.sha256(newkey.encode()).hexdigest()
	newname = ""
	#"http://localhost:8000/doit?name=8cb659e7c6a3741f06c05a470c5d1be19fc06e0e92428683cace4d466dab93fa&action_type=change_key&key=f23fe76e075c152c58b7446f963282c6f719ead3c87207d919f7a1a5b139959b&newkey=new_key"
	x = requests.get(path+"?name="+keyname+"&key="+password+"&newkey="+keyhash+"&action_type=change_key")
	# { "output": "1d02bd8d2550f41376ef49188516c870119dca49e9d8a5ff9649f6211eb2bfb7" }
	myval = json.loads( x.content.decode('utf-8').strip() )

	if len(myval["output"])<=40:
		return [False,"NO_key", "",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	stingout = "key="+newkey+" name="+myval["output"]+" entery_name="+ledgure_name+" path="+path
	#print(stingout)
	return [True,stingout,path+ledgure_name]

#add crypto to user acount
def add_crypto(uname,password,path,key,name,lname,cnx):
	if (usercheck_conect(uname,password,cnx)==False):
		return "No_user"
	is_user=usercheck_conect(uname,password,cnx)
	if is_user=="False" or uname=="NULL":
		dictionary ={ 
		  "response": "NO_user",
		}
		return json.dumps(dictionary, indent = 4)	
	val = [False,path+"check_key.php?name="+key,path+"check_key.php?name="+key,""]
	val = get_key(path,lname,name,key)
	#val = get_key(path,lname,name,key)
	if (val[0]==True):
		random_string=""
		for _ in range(100):
		    random_integer = random.randint(65, 80)
		    random_string += (chr(random_integer))
		passwordCandidate = random_string
		ADD="INSERT INTO `crypto3` (`id_section`, `item_name`, `url`, `added`, `cached`, `used`) VALUES (\'"+random_string+"\', \'"+val[2]+"\', \'"+val[1]+"\', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'NOT');"
		cursor = cnx.cursor()
		cursor.execute(ADD)
		cnx.commit()
		Q0=("SELECT Count(*) FROM `money` WHERE `user_money` LIKE \'"+uname+"_"+val[2]+"\' ")
		cursor = cnx.cursor()
		cursor.execute(Q0)
		for row in cursor:
			number_of_users=row[0]
		if (number_of_users==0):
			query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+uname+"\', \'"+uname+"_"+val[2]+"\', \'"+val[2]+"\', '1');")
			cursor = cnx.cursor()
			cursor.execute(query2)
			cnx.commit()
			dictionary ={ 
			  "response": "1",
			}
			return json.dumps(dictionary, indent = 4)
		else:
			Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+uname+"_"+val[2]+"\'")
			cursor = cnx.cursor()
			cursor.execute(Q0)
			for row in cursor:
				money=row[0]
			amnountleft=money+1
			U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+uname+"_"+val[2]+"';")
			cursor = cnx.cursor()
			cursor.execute(U1)
			cnx.commit()
			dictionary ={ 
			  "response": str(amnountleft),
			}
			return json.dumps(dictionary, indent = 4)	
	else:
		dictionary ={ 
		  "response": "NO_key"+val[1]+" "+val[2],
		}
		return json.dumps(dictionary, indent = 4)

#adds money type to user acount if its not there and makes it zero 
def checkandadd_money_type(user,money,cnx):
	#adds a money collum if there is no money avaible
	Q0=("SELECT Count(*) FROM `money` WHERE `user_money` LIKE \'"+user+"_"+money+"\' ")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		number_of_users=row[0]
	if (number_of_users==0):
		query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+user+"\', \'"+user+"_"+money+"\', \'"+money+"\', '0');")
		cursor = cnx.cursor()
		cursor.execute(query2)
		cnx.commit()
	return

#add crypto to user acount
def add_crypto(uname,password,path,key,name,lname,cnx):
	if (usercheck_conect(uname,password,cnx)==False):
		return "No_user"
	is_user=usercheck_conect(uname,password,cnx)
	if is_user=="False" or uname=="NULL":
		dictionary ={ 
		  "response": "NO_user",
		}
		return json.dumps(dictionary, indent = 4)	
	val = [False,path+"check_key.php?name="+key,path+"check_key.php?name="+key,""]
	try:
		val = get_key2(path,lname,name,key)
	except:
		pass
	#val = get_key(path,lname,name,key)
	if (val[0]==True):
		random_string=""
		for _ in range(100):
		    random_integer = random.randint(65, 80)
		    random_string += (chr(random_integer))
		passwordCandidate = random_string
		ADD="INSERT INTO `crypto3` (`id_section`, `item_name`, `url`, `added`, `cached`, `used`) VALUES (\'"+random_string+"\', \'"+val[2]+"\', \'"+val[1]+"\', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'NOT');"
		cursor = cnx.cursor()
		cursor.execute(ADD)
		cnx.commit()
		Q0=("SELECT Count(*) FROM `money` WHERE `user_money` LIKE \'"+uname+"_"+val[2]+"\' ")
		cursor = cnx.cursor()
		cursor.execute(Q0)
		for row in cursor:
			number_of_users=row[0]
		if (number_of_users==0):
			query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+uname+"\', \'"+uname+"_"+val[2]+"\', \'"+val[2]+"\', '1');")
			cursor = cnx.cursor()
			cursor.execute(query2)
			cnx.commit()
			dictionary ={ 
			  "response": "1",
			}
			return json.dumps(dictionary, indent = 4)
		else:
			Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+uname+"_"+val[2]+"\'")
			cursor = cnx.cursor()
			cursor.execute(Q0)
			for row in cursor:
				money=row[0]
			amnountleft=money+1
			U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+uname+"_"+val[2]+"';")
			cursor = cnx.cursor()
			cursor.execute(U1)
			cnx.commit()
			dictionary ={ 
			  "response": str(amnountleft),
			}
			return json.dumps(dictionary, indent = 4)	
	else:
		dictionary ={ 
		  "response": "NO_key",
		}
		return json.dumps(dictionary, indent = 4)

#adds money type to user acount if its not there and makes it zero 
def checkandadd_money_type(user,money,cnx):
	#adds a money collum if there is no money avaible
	Q0=("SELECT Count(*) FROM `money` WHERE `user_money` LIKE \'"+user+"_"+money+"\' ")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		number_of_users=row[0]
	if (number_of_users==0):
		query2=("INSERT INTO `money` (`user`, `user_money`, `mony_type`, `amount_of_money`) VALUES (\'"+user+"\', \'"+user+"_"+money+"\', \'"+money+"\', '0');")
		cursor = cnx.cursor()
		cursor.execute(query2)
		cnx.commit()
	return

#returns barter curnacy to user 
def get_key_back(uname,password,money_type,cnx):
	if (usercheck_conect(uname,password,cnx)==False):
		return "No_user"
	checkandadd_money_type(uname,money_type,cnx)
	Q0=("SELECT `amount_of_money` FROM `money` WHERE `user_money` LIKE \'"+uname+"_"+money_type+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	for row in cursor:
		money=row[0]
	#subtrask curancy
	amnountleft = money-1
	if amnountleft>=0:
		pass
	else:
		dictionary ={ 
		  "response": "no_funds for " + uname+"_"+money_type,
		}
		return json.dumps(dictionary, indent = 4)
	U1=("UPDATE `money` SET `amount_of_money` = \'"+str(amnountleft)+"\' WHERE `money`.`user_money` = '"+uname+"_"+money_type+"';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()

	U1=("SELECT `id_section`,`url` FROM `crypto3` WHERE `item_name` LIKE \'"+money_type+"\' and  `used` LIKE 'NOT';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()
	for row in cursor:
		stingid=row[0]
		url=row[1]
	U1=("UPDATE `crypto3` SET `used` = 'used' WHERE `id_section` = \'"+stingid+"\';")
	cursor = cnx.cursor()
	cursor.execute(U1)
	cnx.commit()
	dictionary ={ 
	  "response": str(url),
	}
	return json.dumps(dictionary, indent = 4)

#get info about traid
def get_traid(traid_id,cnx):
	Q0="SELECT `traid_id`,`traid_mony_type`,`traid_request_type`,`traid_mony_type`,`traid_request_amount`,`traid_money_amount`,`user`,`buyer` FROM `traidtable` WHERE `traid_id` LIKE \'"+traid_id+"\'; "
	counter=0
	cursor = cnx.cursor()
	cursor.execute(Q0)
	cnx.commit()
	for row in cursor:
		counter=1
		traid_id=row[0]
		traid_mony_type=row[1]
		traid_request_type=row[2]
		traid_request_amount=row[3]
		traid_money_amount=row[4]
		traid_request_amount=row[5]
		user=row[6]
		buyer =row[7]
	if counter==1:
		dictionary ={ 
		  "traid_id": traid_id,
		  "traid_mony_type": traid_mony_type,
		  "traid_request_type":traid_request_type,
		  "traid_request_amount":traid_request_amount,
		  "traid_money_amount":traid_money_amount,
		  "traid_request_amount":traid_request_amount,
		  "user":user,
		  "buyer":buyer
		}
		return json.dumps(dictionary, indent = 4)
		#return str(traid_id)+" "+str(traid_mony_type)+" "+str(traid_request_type)+" "+str(traid_request_amount)+" "+str(traid_money_amount)+" "+str(traid_request_amount)+" "+str(user)+" "+str(buyer)
	dictionary ={ 
	  "traid_id": "NO_traid_id",
	  "traid_mony_type": "NA",
	  "traid_request_type":"NA",
	  "traid_request_amount":"NA",
	  "traid_money_amount":"NA",
	  "traid_request_amount":"NA",
	  "user":"NA",
	  "buyer":"NA"
	}
	return json.dumps(dictionary, indent = 4)

#prints infro about user
def user_acount(user,cnx):
	if user=="NULL":
		return "False_NO_NULL_user"
	Q0=("SELECT `user_money`,`amount_of_money` FROM `money` WHERE `user` LIKE \'"+user+"\'")
	cursor = cnx.cursor()
	cursor.execute(Q0)
	cnx.commit()
	outsting=[]
	for row in cursor:
		outsting=outsting+[ [row[0],str(row[1])] ]
	cnx.commit()
	cnx.close()
	dictionary ={ 
	  "out": outsting,
	}
	return json.dumps(dictionary, indent = 4)

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
    use_key=""
    try:
        use_key=req.GET["use_key"]
    except:
        pass
    try:
        use_key=req.GET["usekkey"]

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
    url=""
    try:
        url=req.GET["url"]
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
    send_type=""
    try:
        send_type=req.GET["send_type"]
    except:
        pass
    send_amount=""

    try:
        send_amount=float(req.GET["send_amount"])
    except:
        pass

    crypto_path=""
    try:
        crypto_path=req.GET["crypto_path"]
    except:
        pass
    traid_id=""
    try:
        traid_id=req.GET["traid_id"]
    except:
        pass
    request_amound=""
    try:
        request_amound=float(req.GET["request_amound"])
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
    if action_type=="url":
        return HttpResponse( under_call(url) )
    if action_type=="adduser":
        out=add_user(user,password,email,try_to_connect(),return_var_type)
        return HttpResponse( out )
    #Getting values
    if action_type=="add_post":
    	return  HttpResponse(add_post(user,password,tital,text,body,photo,catagoy,catagoy_2,iframe, try_to_connect(),return_var_type ) )
    if action_type=="get_post":
    	return  HttpResponse( getpost(key,use_key,try_to_connect(),return_var_type ) )
    if action_type=="add_ledgure":
    	return HttpResponse( add_ledgure(user,password,email,hashword,Ledgure,try_to_connect() ,return_var_type ) )
    if action_type=="add_key":
    	return HttpResponse(  add_key(ledgure,password,email,message,key_message,keyfroward, try_to_connect() ,return_var_type ) )
    if action_type=="change_post":
    	return HttpResponse( change_post(user,password,key,text,try_to_connect() ,return_var_type ) )
    if action_type =="change_key":
    	return HttpResponse( change_key(key,name,newkey,try_to_connect(),return_var_type ) )
    if action_type =="check_key":
    	return HttpResponse( check_key(name,try_to_connect(),return_var_type ) )
    if action_type =="rm_key":
    	return HttpResponse( rm_key(name,key,L_name,try_to_connect(),return_var_type ) )
    if action_type=="fintraid":
        return HttpResponse( compleat_traid_comand(user,password,traid_id,try_to_connect()) )
    if action_type=="Uprint":
    	return HttpResponse(  user_acount(user,try_to_connect()) )
    if action_type=="traid":
    	return HttpResponse( get_traid(traid_id,try_to_connect()) )
    if action_type=="add_C":
        return HttpResponse(add_crypto(user,password,crypto_path,crypto_key,crypto_name,L_name,try_to_connect()) )
    if action_type=="get_C":
        return HttpResponse(get_key_back(user,password,crypto_path+L_name,try_to_connect()))
    if action_type=="maketraid":
        return HttpResponse( funtion_make_traid(user,password,send_type,send_amount,request_type,request_amound,try_to_connect())  )
    a=""
    try:
        a=req.GET["a"]
    except:
        pass
    if a =="re":
    	return redirect_req(url,rep,try_to_connect())
    #templates
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

    if action_type=="makepage":
        if setion==""  or setion2=="":
            if setion=="":
                    randome2 = get_random_string(128)
                    setion = hashlib.sha256(randome2.encode()).hexdigest()
                    try:
                    	make_setion(setion, try_to_connect() )
                    except:
                    	pass
            if setion2=="":
                    randome2 = get_random_string(128)
                    setion2 = hashlib.sha256(randome2.encode()).hexdigest()
                    try:
                        make_setion(setion2, try_to_connect() )
                    except:
                    	pass

            response = redirect('http://localhost:8000/doit?action_type=makepage&usertemplate_name='+usertemplate_name+'&var1='+var1+'&rep='+rep+'&setion='+setion+'&setion2='+setion2)
            return response
        else:
            return HttpResponse(return_template(usertemplate_name,var1,setion,setion2,rep,try_to_connect() ) )
    return HttpResponse( "api_fail" )



def get_key(path,ledgure_name,keyname,password):
	#get barter key
	x = requests.get(path+"check_key.php?name="+keyname)

	getarray = str(x.content)

	out = getarray.split(" ")
	if len(out)==9:
	#cehcks barter key
		print("passed_leddgure")
	else:
		return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]

	if ledgure_name==out[1]:
		print("passed_leddgure")
	else:
		return [False,"Failed leddgure",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	#
	passwordCandidate = password
	val = hashlib.sha256(passwordCandidate.encode()).hexdigest()
	if val==out[3]:
		print("passed_key")
	else:
		return [False,"Failed_key",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	random_string=""
	#generate and sores new crypto
	for _ in range(100):
	    random_integer = random.randint(65, 80)
	    random_string += (chr(random_integer))
	passwordCandidate = random_string
	newkey = hashlib.sha256(passwordCandidate.encode()).hexdigest()
	keyhash = hashlib.sha256(newkey.encode()).hexdigest()
	newname = ""
	x = requests.get(path+"change_key.php?name="+keyname+"&key="+password+"&Nkey="+keyhash)
	myval = x.content.decode('utf-8').strip()

	if myval=="false":
		return [False,"NO_key", "",path+" "+ledgure_name+" "+keyname+" "+password+" "+path+"check_key.php?name="+keyname]
	stingout = path+"output2.php?key="+newkey+"&name="+myval+"&entery_name="+ledgure_name 
	#print(stingout)
	return [True,stingout,path+ledgure_name]

