#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
from google.appengine.api import users
import logging
from datastore_obj import WageStub, PaycheckStub, User
from time_calc_funct import time_calc
from datetime import datetime

env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        main_template = env.get_template('main.html')

        #
        user = users.get_current_user()
        if user:
            greet = ('<a href="%s">Log out</a>') % (users.create_logout_url('/'))
            finlog_button = ("<a href='finlog'>Financial Calculator</a>")
            logpage_button = ("<a href='logpage'>Finance Log</a>")
        else:
            greet = ('<a href="%s">Log in</a>') % (users.create_login_url('/'))
            finlog_button = ""
            logpage_button= ""



        greetingdict = {'signout':greet,'finlogbutton':finlog_button,'logpagebutton':logpage_button}
        logging.info(greetingdict)
        self.response.write(main_template.render(greetingdict))

class FinancialCalcHandler(webapp2.RequestHandler):
    def get(self):
        f_template = env.get_template('finlog.html')

        # Generating Signout Link
        user=users.get_current_user()
        signout_greeting = ('<a href="%s">Log Out</a>') % (users.create_logout_url('/'))

        # Financial Log Dictionary
        financial_log_dict = {'signout':signout_greeting}

        self.response.write(f_template.render(financial_log_dict))

    def post(self):
        f_template = env.get_template('finlog.html')

        # Generating Signout Link
        user=users.get_current_user()
        signout_greeting = ('<a href="%s">Log Out</a>') % (users.create_logout_url('/'))

        #Request the Wage Variables
        clock_in_hour = int(self.request.get('time_in_hour'))
        clock_in_min = int(self.request.get('time_in_min'))
        time_of_day_in = (self.request.get('time_of_day_in'))

        clock_out_hour = int(self.request.get('time_out_hour'))
        clock_out_min = int(self.request.get('time_out_min'))
        time_of_day_out = (self.request.get('time_of_day_out'))

        break_time_length = int(self.request.get('break_time_length'))

        date = self.request.get('date')
        date_obj = datetime.strptime(date, '%Y-%m-%d')

        marital_status = int(self.request.get('marital_status'))
        userID = user.user_id()

        #Total Time Worked (NOT NECESSARY ANYMORE):
        time_worked = time_calc(clock_in_hour,clock_out_hour,clock_in_min,clock_out_min,time_of_day_in,time_of_day_out) - (break_time_length/60.0)

        total_tax = 0
        if marital_status == 2:
            total_tax = 6.20 + 1.45 + 0.90
        else:
            total_tax = 6.20 + 1.45 + 0.90 + 1.315

        # Check if user is in database: if not create datastore element; otherwise simply modify
        user_query_result = User.query(User.user_id==userID).get()

        if not user_query_result:
            (User(user_id=userID,marital_status=marital_status,total_california_tax=total_tax)).put()

        logging.info(date_obj)
        (WageStub(clock_in_hour=clock_in_hour,
            clock_in_min=clock_in_min,
            time_of_day_in=time_of_day_in,
            clock_out_hour=clock_out_hour,
            clock_out_min=clock_out_min,
            time_of_day_out=time_of_day_out,
            break_time_length=break_time_length,
            date=date_obj,
            user_id=userID)).put()

        #ARE THE FIRST TWO VARIABLES NECESSARY??
        financial_log_dict  = {'time_worked': time_worked,'total_california_tax':total_tax,'signout':signout_greeting}
        self.response.write(f_template.render(financial_log_dict))

def objCon(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d').date()

class FinancialCalcCheckHandler(webapp2.RequestHandler):
    def post(self):
        f_template = env.get_template('finlog.html')

        # Generating Signout Link
        user=users.get_current_user()
        userID = user.user_id()
        signout_greeting = ('<a href="%s">Log Out</a>') % (users.create_logout_url('/'))

        #Request variables
        start_date = self.request.get('start_date')
        start_date_obj = objCon(start_date)
        end_date = self.request.get('end_date')
        end_date_obj = objCon(end_date)

        pay_check = float(self.request.get('pay_check'))
        #code: #1: ok; #2: not ok
        alert_notification = 0

        #Compare pay_check vs wage_stubs
        #Check if user submitting a check is in database
        user_query_result = User.query(User.user_id==userID).get()
        if not user_query_result:
            alert_notification = 0
        else:
            (PaycheckStub(
                pay_check = pay_check,
                user_id = userID,
                start_date = start_date_obj,
                end_date = end_date_obj,
            )).put()

            wage_stubs_query_results = WageStub.query(WageStub.user_id==userID, WageStub.date >= start_date_obj, WageStub.date <= end_date_obj).fetch()
            total_time_worked = 0
            estimated_pay = 0
            for wageStubs in wage_stubs_query_results:
                total_time_worked += time_calc(wageStubs.clock_in_hour,wageStubs.clock_out_hour,wageStubs.clock_in_min,wageStubs.clock_out_min,wageStubs.time_of_day_in,wageStubs.time_of_day_out)
            if user_query_result.user_id == userID:
                estimated_pay = (total_time_worked * 10.50) - (((user_query_result.total_california_tax)/100)*(total_time_worked * 10.50))
                if  pay_check < estimated_pay-1:
                    alert_notification = 2
                else:
                    alert_notification = 1
            else:
                self.response.write('user is not in database!')

        financial_log_dict = {
        #REMEMBER TO PUT A COMMA
                'alert':alert_notification,
                 'pay_check':pay_check,
                 'estimated_pay':round(estimated_pay,2),
                 'signout': signout_greeting
                }
        self.response.write(f_template.render(financial_log_dict))

class FinancialLogHandler(webapp2.RequestHandler):
    def get(self):
        main_template = env.get_template('log.html')

        #
        user = users.get_current_user()
        userID = user.user_id()
        if user:
            greet = ('<a href="%s">Log out</a>') % (users.create_logout_url('/'))
            finlog_button = ("<a href='finlog'>Financial Calculator</a>")
        else:
            greet = ('<a href="%s">Log in</a>') % (users.create_login_url('/'))
            finlog_button = ""

        #Retrieves ALL the wage stubs (no paycheck stubs) but not in chronological order!!
        wage_stubs_query_results = WageStub.query(WageStub.user_id==userID).order(-WageStub.date).fetch()
        paycheck_stubs_query_results = PaycheckStub.query(PaycheckStub.user_id==userID).order(-PaycheckStub.start_date).fetch()


        stubs_list = []
        if len(wage_stubs_query_results) >= len(paycheck_stubs_query_results):
            paycheck_index = 0
            for wage_stubs in wage_stubs_query_results:
                # FIX THE CHRONO ISSUE
                if paycheck_index == len(paycheck_stubs_query_results):
                    stubs_list.append(wage_stubs)
                    logging.info('IF ===')
                    logging.info(stubs_list)
                elif wage_stubs.date > paycheck_stubs_query_results[paycheck_index].end_date:
                    stubs_list.append(wage_stubs)
                    logging.info('ELIF ===')
                    logging.info(stubs_list)
                else:
                    stubs_list.append(paycheck_stubs_query_results[paycheck_index])
                    stubs_list.append(wage_stubs)
                    logging.info('ELSE ===')
                    logging.info(stubs_list)
                    paycheck_index+=1
        else:
            wagestub_index = 0
            for paycheck in paycheck_stubs_query_results:
                if wagestub_index == len(wage_stubs_query_results):
                    stubs_list.append(paycheck)
                    logging.info('IF ===')
                elif paycheck.end_date > wage_stubs_query_results[wagestub_index].date:
                    stubs_list.append(paycheck)
                else:
                    stubs_list.append(wage_stubs_query_results[wagestub_index])
                    stubs_list.append(paycheck)
                    wagestub_index+=1

        logging.info('STUBS_LIST======')
        logging.info(stubs_list)

        greetingdict = {'signout':greet,'finlogbutton':finlog_button,'stubs':stubs_list}
        logging.info(greetingdict)
        self.response.write(main_template.render(greetingdict))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/finlog',FinancialCalcHandler),
    ('/finlog-check',FinancialCalcCheckHandler),
    ('/logpage',FinancialLogHandler)
], debug=True)
