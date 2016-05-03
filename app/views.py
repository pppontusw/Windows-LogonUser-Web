from app import app, db
import subprocess
import flask
from flask import render_template, flash, redirect
from .forms import SearchForm, AddComputerForm
import re
from .models import User, Computer
import datetime
import time

#app = flask.Flask(__name__)

def getComputerInfo(computername):
	searchform = SearchForm()
	addcomputerform = AddComputerForm()
	computerstring = '/server:' + computername
	# call subprocess
	sproc = subprocess.Popen(["quser", computerstring], stdout=subprocess.PIPE)
	# read stdout
	outp = sproc.stdout.readlines()
	# initialize object to hold the utf8 list
	outps = []
	# wait for the subprocess call to finish
	sproc.wait()
	for output in outp:
		# make the list in utf8
		outps.append(output.decode('utf-8'))
	# construct the object that will hold all our users
	userobj = []
	# if this fails we probably did not get a correct response from the server
	try:
		# removing the first line as we will print that in our HTML
		del outps[0]
	except IndexError:
		return render_template('admin.html', addcomputerform=addcomputerform, searchform=searchform, error='We could not give you results for ' + computername + ', please check that this name is correct.', addcomps=True)
	# go through our users to construct the object
	for user in outps:
		userattr = user.split()
		# for users where the session name is missing
		if (len(userattr) == 6):
			# assemble timestamp
			logtime = userattr[4] + " " + userattr[5]
			# disc is not quite descriptive enough
			if (userattr[2] == 'Disc'):
				userattr[2] = 'Disconnected'
			# assemble and append the object
			userconstr = { 'name': userattr[0], 'session': 'N/A', 'id': userattr[1], 'state': userattr[2], 'idle': userattr[3], 'logon': logtime }
			userobj.append(userconstr)
		# if we have a session name this array will be 7 chars
		elif (len(userattr) == 7):
			# assemble timestamp
			logtime = userattr[5] + " " + userattr[6]
			# disc is not quite descriptive enough
			if (userattr[3] == 'Disc'):
				userattr[3] = 'Disconnected'
			# assemble and append the object
			userconstr = { 'name': userattr[0], 'session': userattr[1], 'id': userattr[2], 'state': userattr[3], 'idle': userattr[4], 'logon': logtime }
			userobj.append(userconstr)
	return userobj

@app.route('/delete/<computername>', methods=['GET'])
def deleteComputer(computername):
	computer = Computer.query.filter_by(computername=computername).first()
	db.session.delete(computer)
	db.session.commit()
	return redirect('/admin')

@app.route('/refreshall', methods=['GET'])
def refreshAll():
	allcomps = Computer.query.all()
	for computer in allcomps:
		userinfo = getComputerInfo(computer.computername)
		if (type(userinfo) == str):
			pass
		else:
			activeusernames = ""
			inactiveusernames = ""
			for user in userinfo:
				if (user['state'] == 'Active'):
					activeusernames = activeusernames + ', ' + user['name']
				else:
					inactiveusernames = inactiveusernames + ', ' + user['name']
			computer.activeusers=activeusernames[1:]
			computer.inactiveusers=inactiveusernames[1:]
			computer.timestamp=datetime.datetime.utcnow()
			db.session.commit()
	return redirect('/')

@app.route('/admin', methods=['GET', 'POST'])
def addComputer():
	searchform = SearchForm()
	addcomputerform = AddComputerForm()
	allcomputers = Computer.query.order_by('computername asc').all()
	if addcomputerform.validate_on_submit():
		computer = Computer.query.filter_by(computername=addcomputerform.data['addcomputer']).first()
		if computer is None:
			userinfo = getComputerInfo(addcomputerform.data['addcomputer'])
			if (type(userinfo) == str):
				return render_template('admin.html', searchform=searchform, addcomputerform=addcomputerform, error='We could not contact ' + addcomputerform.data['addcomputer'] + ', please check that the computer name is correct.', allcomputers=allcomputers, addcomps=True)
			activeusernames = ""
			inactiveusernames = ""
			for user in userinfo:
				if (user['state'] == 'Active'):
					activeusernames = activeusernames + ', ' + user['name']
				else:
					inactiveusernames = inactiveusernames + ', ' + user['name']
			computer = Computer(computername=addcomputerform.data['addcomputer'], activeusers=activeusernames[1:], inactiveusers=inactiveusernames[1:], timestamp=datetime.datetime.utcnow())
			db.session.add(computer)
			db.session.commit()
			allcomputers = Computer.query.order_by('computername asc').all()
		else:
			return render_template('admin.html', searchform=searchform, addcomputerform=addcomputerform, error='Already exists.', allcomputers=allcomputers, addcomps=True)
	return render_template('admin.html', searchform=searchform, addcomputerform=addcomputerform, allcomputers=allcomputers, addcomps=True)


@app.route('/<computername>', methods=['GET'])
def getComputer(computername):
	searchform = SearchForm()
	computer = Computer.query.filter_by(computername=computername).first()
	userobj = getComputerInfo(computername)
	if (type(userobj) == str):
		allcomputers = Computer.query.order_by('computername asc').all()
		return render_template('index.html', searchform=searchform, error='We could not contact ' + computername + ', please check that the computer name is correct.', allcomputers=allcomputers, listcomps=True)
	activeusernames = ""
	inactiveusernames = ""
	for user in userobj:
		if (user['state'] == 'Active'):
			activeusernames = activeusernames + ', ' + user['name']
		else:
			inactiveusernames = inactiveusernames + ', ' + user['name']
	if computer is None:
		newcomputer = Computer(computername=computername, activeusers=activeusernames[1:], inactiveusers=inactiveusernames[1:], timestamp=datetime.datetime.utcnow())
		db.session.add(newcomputer)
	else:
		computer.activeusers=activeusernames[1:]
		computer.inactiveusers=inactiveusernames[1:]
		computer.timestamp=datetime.datetime.utcnow()
	db.session.commit()
	return render_template('users.html', users=userobj, searchform=searchform, computername=computername)

@app.route('/')
def index():
	searchform = SearchForm()
	allcomputers = Computer.query.order_by('computername asc').all()
	return render_template('index.html',
							searchform=searchform,
							allcomputers=allcomputers,
							listcomps=True)

@app.route('/search', methods=['POST'])
def search():
	form = SearchForm()
	allcomputers = Computer.query.order_by('computername asc').all()
	if form.validate_on_submit():
		computername = form.data['findcomputer']
		return flask.redirect(flask.url_for('getComputer', computername=computername))
	else:
		return render_template('index.html', searchform=form, listcomps=True, allcomputers=allcomputers, error="Search field cannot be empty")