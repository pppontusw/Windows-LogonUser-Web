#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app, views

def test_home_page():
    client = app.test_client()
    rsp = client.get('/')
    assert rsp.status == '200 OK'
    html = rsp.get_data(as_text=True)
    assert '<th> Computer Name <a class="glyphicon glyphicon-sort sort pull-right" data-sort="computername"></a></th>' in html
    assert '<th><a class="glyphicon glyphicon-sort sort pull-right" data-sort="activeusers"></a> Active Users</th>' in html
    assert '<th><a class="glyphicon glyphicon-sort sort pull-right" data-sort="inactiveusers"></a> Inactive Users</th>' in html
    assert '<th> Last Updated</th>' in html

def test_admin_page():
    client = app.test_client()
    rsp = client.get('/admin')
    assert rsp.status == '200 OK'
    html = rsp.get_data(as_text=True)
    assert '<input class="form-control" id="addcomputer" name="addcomputer" placeholder="Computer name" type="text" value="">' in html
    assert '<button type="submit" class="btn btn-default" type="button">Add</button>' in html
    assert '<h4>Remove computers</h4><br>' in html

def test_get_computer():
    client = app.test_client()
    rsp = client.get('/localhost')
    assert rsp.status == '200 OK'
