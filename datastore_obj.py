from google.appengine.ext import ndb
#marital status code:
#1: Dual Income or Single: 1.315%
#2: Married (1 income): 0%
#3: Head of Household: 1.315%

class User(ndb.Model):
    user_id = ndb.StringProperty()
    # time_worked = ndb.FloatProperty()
    marital_status = ndb.IntegerProperty()
    total_california_tax = ndb.FloatProperty()

class WageStub(ndb.Model):
    clock_in_hour = ndb.IntegerProperty()
    clock_in_min = ndb.IntegerProperty()
    time_of_day_in = ndb.StringProperty()
    clock_out_hour = ndb.IntegerProperty()
    clock_out_min = ndb.IntegerProperty()
    time_of_day_out = ndb.StringProperty()
    break_time_length = ndb.FloatProperty()
    date = ndb.DateProperty()
    user_id = ndb.StringProperty()

class PaycheckStub(ndb.Model):
    pay_check = ndb.FloatProperty()
    user_id = ndb.StringProperty()
    start_date = ndb.DateProperty()
    end_date = ndb.DateProperty()
