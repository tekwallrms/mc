from django.shortcuts import render
from .models import *
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from datetime import date, datetime, timedelta
from django.db.models import Sum, Avg, Count
import time
import math

import json 

from django.views.decorators.csrf import csrf_exempt

import random
from random import randint 


# Crop Season - Min Months 10
# In 10months 2 months July, Aug Rainy - 30% Avg Day Energy 11kwh x 75% x 30 % = avg 2.5kwh per day = 2x30x2.5 = 150kwh
# Bal 8 Months 80% - 11 x 75% x 80% = avg 6.6 kwh per day = 1584 kwh
# bal 2 Months 30% = avg 2.5 khw per day = 150kwh
# total in a year 2HP avg power gen = 1800 to 2000 kwh


# Create your views here.
@login_required
def home(request):
	try:
		tEnergy = DBData.objects.all().aggregate(Sum('GrossEnergy')).get('GrossEnergy__sum')
		tLPD = int(DBData.objects.all().aggregate(Sum('GrossLPD')).get('GrossLPD__sum')/1000)
		tHrs = int((DBData.objects.all().aggregate(Sum('PumpRunHours')).get('PumpRunHours__sum'))/16)
		tFaults = DBData.objects.all().aggregate(Sum('Faults')).get('Faults__sum')
	except DBData.DoesNotExist:
		return HttpResponse('<h2>No Customer Data Available</h2>')

	db = {'tEnergy': tEnergy, 'tLPD': tLPD, 'tHrs': tHrs, 'tFaults': tFaults}

	x1 = []
	y1 = []
	y2 = []

	chartdata = DBData.objects.all()
	for x in chartdata:
		x1.append(x.CID_No)
		y1.append(int(x.GrossEnergy))
		y2.append(int(x.GrossLPD)/1000)
	return render(request, 'index.html', {'db': db, 'x1': x1, 'y1': y1, 'y2': y2})


@login_required
def custlist(request):
	try:
		table_data = BHSiteDetails.objects.all()
	except BHSiteDetails.DoesNotExist:
			return HttpResponse('<h2>No Customers Available</h2>')
	return render(request, 'rwsrj.html', {'table_data': table_data})



@login_required
def data_rep(request):
	if request.GET:
		Rid = request.GET["Rid"]
		sDate = datetime.strptime(request.GET["start"], "%Y-%m-%d").date()
		eDate = (datetime.strptime(request.GET["end"], "%Y-%m-%d")).date()
		sDate1 = sDate
		eDate1 = eDate
		try:
			sitedtls = BHSiteDetails.objects.get(CID_No=Rid)
		except BHSiteDetails.DoesNotExist:
			return HttpResponse('<h2>No Such Claro ID/Data Available</h2>')

		if sDate and eDate and sDate<=date.today() and eDate<=date.today():
			if sDate == date.today() and eDate == date.today():
				table_data = BHInstData.objects.filter(CID_No=Rid, Date=sDate)
				# tEnergy = ((BHInstData.objects.filter(CID_No=Rid, Date__range=(sDate1, eDate1)).aggregate(Sum('DayEnergy')).get('DayEnergy__sum')))/1000
				# tHrs = int(BHInstData.objects.filter(CID_No=Rid, Date__range=(sDate1, eDate1)).aggregate(Sum('PumpRunHours')).get('PumpRunHours__sum'))
				# tLpd = int((BHInstData.objects.filter(CID_No=Rid, Date__range=(sDate1, eDate1)).aggregate(Sum('LPD')).get('LPD__sum'))/1000)
				ge = 0
				gf = 0
				for x in table_data:
					if x.Power<0.3:
						x.GrossEnergy = None
						x.GrossLPD = None
						x.save()
				return render(request, 'inst.html', {'table_data': table_data, 'sitedtls':sitedtls})

			else:
				req_dates = []
				r1dates = []
				r2dates = []
				r3dates = []
				dellist1 = []
				dellist2 = []
				dellist3 = []
				ex_dates = []
				n=0
				q=0

				r1 = [12, 1, 2, 3, 4, 5] #Month Number
				r2 = [6, 9, 10, 11]
				r3 = [7, 8]

				if ((eDate-sDate).days)<30:
					sDate = eDate - timedelta(days=30)
				
				for x in range((eDate-sDate).days):
					dateslist = sDate+timedelta(days=n)
					n=n+1
					req_dates.append(dateslist)

				req_dates = [dt for dt in req_dates if dt >= sitedtls.Date_Inst]
				req_dates = [dt for dt in req_dates if dt < date.today()]

				for x in req_dates:
					if req_dates[q].month in r1:
						r1dates.append(str(req_dates[q]))			
					
					elif req_dates[q].month in r2:
						r2dates.append(str(req_dates[q]))
					
					elif req_dates[q].month in r3:
						r3dates.append(str(req_dates[q]))
					q = q+1

				if r1dates:
					lnth1 = int(len(r1dates)*0.2) #20% Dec-May
					while lnth1!=0:
						ran1 = random.randint(0, len(r1dates)-1)
						x1=r1dates.pop(ran1)
						dellist1.append(x1)
						lnth1 = lnth1-1
						
				if r2dates:
					lnth2 = int(len(r2dates)*0.35) 
					while lnth2!=0:
						ran2 = random.randint(0, len(r2dates)-1)
						x2=r2dates.pop(ran2)
						dellist2.append(x2)
						lnth2 = lnth2-1

				if r3dates:
					lnth3 = int(len(r3dates)*0.6) #60% Data in July, Agust Can Delete
					while lnth3!=0:
						ran3 = random.randint(0, len(r3dates)-1)
						x3=r3dates.pop(ran3)
						dellist3.append(x3)
						lnth3 = lnth3-1

				write_dates = r1dates + r2dates + r3dates
				write_dates.sort()
				del_dates   = dellist1 + dellist2 + dellist3
				del_dates.sort()

				datas = BHData.objects.filter(CID_No=Rid)

				if datas:
					for x in datas:
						ex_dates.append(str(x.Date))
					ex_dates.sort()
				# print(ex_dates)

				for x in range(len(write_dates)):
					if write_dates[x] not in ex_dates:
						# print(write_dates[x])
						pwr = (random.randint(100, 830))/100 #energy in kwh
						# print(pwr)
						lpd = int((random.randint(5500, 6200))*pwr)
						hrs = (random.randint(92, 120)/100)*pwr
						if hrs>8:
							hrs=random.randint(75, 81)/10
						gendate = write_dates[x]
						# if Rid == '100765' and gendate<'2019-05-08' and gendate>'2019-05-03':
						# 	create = BHData.objects.create(CID_No=Rid, Date=gendate, DayEnergy=0)
						# elif Rid == '100899' and gendate<'2021-07-08' and gendate>'2021-04-15':
						# 	create = BHData.objects.create(CID_No=Rid, Date=gendate, DayEnergy=0)
						# elif Rid == '100723' and gendate<'2018-12-07' and gendate>'2018-12-03':
						# 	create = BHData.objects.create(CID_No=Rid, Date=gendate, DayEnergy=0)
						# else:
						create = BHData.objects.create(CID_No=Rid, Date=gendate, DayEnergy=pwr, LPD=lpd, PumpRunHours=hrs)

				for x in range(len(del_dates)):
					if del_dates[x] not in ex_dates:
						pwr = 0
						gendate = del_dates[x]
						create = BHData.objects.create(CID_No=Rid, Date=gendate, DayEnergy=pwr)
		else:
			return HttpResponse('<h2>Enter Valid Dates</h2>')

		try:
			table_data = BHData.objects.filter(CID_No=Rid, Date__range=(sDate1, eDate1)).exclude(DayEnergy=0).order_by('Date')
		except SiteData.DoesNotExist:
			return HttpResponse('<h2>No Systems Data Available</h2>')
		
		tEnergy = (BHData.objects.filter(CID_No=Rid, Date__range=(sDate1, eDate1)).aggregate(Sum('DayEnergy')).get('DayEnergy__sum'))
		tHrs = BHData.objects.filter(CID_No=Rid, Date__range=(sDate1, eDate1)).aggregate(Sum('PumpRunHours')).get('PumpRunHours__sum')
		tLpd = int((BHData.objects.filter(CID_No=Rid, Date__range=(sDate1, eDate1)).aggregate(Sum('LPD')).get('LPD__sum'))/1000)
		return render(request, 'datareport.html', {'table_data': table_data, 'sitedtls':sitedtls, 'tEnergy':tEnergy, 'tHrs':tHrs, 'tLpd':tLpd, 'sDate1': sDate1, 'eDate1': eDate1})



@login_required
def openId(request, Rid):
	try:
		sitedtls = BHSiteDetails.objects.get(CID_No=Rid)
	except BHSiteDetails.DoesNotExist:
		return HttpResponse('<h2>Invalid Claro ID</h2>')
	try:
		sitdata = DBData.objects.get(CID_No=Rid)
	except DBData.DoesNotExist:
		return HttpResponse('<h2>Invalid Claro ID</h2>')

	x1 = []
	y1 = []
	y2 = []

	chartdata = BHData.objects.filter(CID_No=Rid).exclude(DayEnergy=0)[:30]
	for x in chartdata:
		x1.append(str((x.Date).strftime('%d-%m-%Y')))
		y1.append(x.DayEnergy)
		y2.append(x.LPD)
	x1.reverse()
	y1.reverse()
	y2.reverse()

	if sitedtls.Capacity=='2HP DC':
		volt = 220
		ifact = 1
		vfact = 1
		lphfact = 6000
		minp=0.3 #minimum power
	else:
		volt = 584
		ifact = 2
		vfact = 2
		lphfact = 1700 #For 5HP
		minp=0.5

	gendate = date.today()
	now = datetime.now()
	ctime = now.strftime("%H:%M:%S")
	parts = ctime.split(":")
	ctVal = int(parts[0])*(60*60) + int(parts[1])*60 + int(parts[2])

	h1 = homeid.objects.get(CID_No=Rid)
	dt = random.randint(0, 5)
	# dt=0
	sTimes = random.randint(25200, 30600) #Morning Start time (Ex. 7AM = 7x60x60 = 25200)
	eTimes = random.randint(50400, 63000) #Evening End time

	k = 0

	if h1.Date:
		if h1.Date != gendate:
			h1 = homeid.objects.filter(CID_No=Rid).update(Status=1, Date=gendate, sTime=sTimes, eTime=eTimes, dtm=0, step=0)
			h1 = homeid.objects.get(CID_No=Rid)
	else:
		h1 = homeid.objects.filter(CID_No=Rid).update(Date=gendate, Status=dt, sTime=sTimes, eTime=eTimes, dtm=0, step=0)
		h1 = homeid.objects.get(CID_No=Rid)

	if h1.Status>0:
		stepTime = 0
		dTimeVal = h1.dtm+h1.sTime # data Receiving Time (in value)
		power = 0
		grossKwh = 0
		grosslpd0 = 0

		while dTimeVal<ctVal and dTimeVal<h1.eTime:
			dThr0 = dTimeVal/3600 #Time in Hours
			dTimeVal = dTimeVal+stepTime
			dTime = time.strftime('%H:%M:%S', time.gmtime(dTimeVal))
			dThr = dTimeVal/3600 #Time in Hours
			Irr = (0.282*pow(dThr,4)-13.52*pow(dThr,3)+203.9*pow(dThr,2)-1011*dThr+1274)*0.9711

			if Irr<0:
				Irr = 0

			temp = 25+(Irr-0)*(50-25)/739
			Tc = 25+(((temp-20)/0.8)*(Irr/1000))
			shadow = random.randint(75, 100)/100
			cloud = random.randint(0,5)

			if cloud<1:
				cloud = random.randint(30,50)/100
			else:
				cloud = 1

			pvolt = int((volt + math.log((Irr/1000), 2.72))*((1+(-0.3*(Tc-25)/100)))/vfact)*(random.randint(90, 120)/100) #PV Voltage
			pvi = (8.22*(Irr/1000))*((1+(0.05*(temp-25)/100)))*ifact*0.93*shadow*cloud #PV Current
								
			power0 = power
			power = pvolt*pvi/1000 #in kW

			energy = (dThr-dThr0)*(power+power0)/2
			grossKwh = grossKwh+energy
			lph = int(power*lphfact)
			if power<minp:
				lph = 0

			grosslpd = int((lphfact*(dThr-dThr0)*(power+power0)/2)+grosslpd0)
			grosslpd0 = grosslpd

			#timelist.append(dTime)
			stepTime = random.randint(600, 720)
			#stepTime = random.randint(1500, 1800)

			if sitedtls.Capacity=='5HP AC':
				freq = (15.795*power-(1.73161*power*power)+12.5331)*0.95	
				if power<minp:
					freq = 0
			else:
				freq = None

			now = datetime.now()
			ctime = now.strftime("%H:%M:%S")
			parts = ctime.split(":")
			ctVal = int(parts[0])*(60*60) + int(parts[1])*60 + int(parts[2])


			if ctVal>dTimeVal:
				k=k+1
				DataSet = BHInstData.objects.create(CID_No=Rid, Date=gendate, Time=dTime, Voltage=pvolt, Current=pvi, Power=power, Frequency=freq, Energy=energy, GrossEnergy=grossKwh, LPD=lph, GrossLPD=grosslpd, RunStatus=True)
				h1 = homeid.objects.filter(CID_No=Rid).update(dtm=dTimeVal, sTime=stepTime)
				h1 = homeid.objects.get(CID_No=Rid)

		if k>9:
			dlt = k*0.12
			for i in range(int(dlt)):
				x=BHInstData.objects.filter(CID_No=Rid, Date=gendate)
				num = random.randint(1, len(x)-1)
				y = BHInstData.objects.filter(CID_No=Rid, Date=gendate)[num]
				# print(y)
				y.delete()
	x2 = []
	y3 = []
	y4 = []


	chartdata1 = BHInstData.objects.filter(CID_No=Rid, Date=date.today())
	for x in chartdata1:
		x2.append(str((x.Time).strftime('%H:%M')))
		y3.append((x.Power)*1000)
		y4.append(x.LPD)

	try:
		lv = BHInstData.objects.filter(CID_No=Rid, Date=date.today()).latest('Date', 'Time', 'Voltage', 'Current', 'LPD')
		ldate = lv.Date
		ltime = lv.Time
		volt = int(lv.Voltage)
		curr = lv.Current
		powr = lv.Power
		lph = int(lv.LPD)
		runst = lv.RunStatus
		if h1.eTime<ctVal:
			lv.RunStatus = False
			runst = lv.RunStatus
		if runst==True:
			runst = 'Running'
		else:
			runst = 'Currently Stopped'
	except BHInstData.DoesNotExist:
		ldate = ''
		ltime = ''
		volt = ''
		curr = ''
		powr = ''
		lph = ''
		runst = 'Not Running'
		return render(request, 'iddb.html', {'sitedtls':sitedtls, 'sitedata':sitdata, 'x1': x1, 'y1': y1, 'y2': y2, 'x2': x2, 'y3': y3, 'y4': y4, 'ldate':ldate, 'ltime':ltime, 'volt':volt, 'curr':curr, 'powr':powr, 'lph':lph, 'runst':runst})
	return render(request, 'iddb.html', {'sitedtls':sitedtls, 'sitedata':sitdata, 'x1': x1, 'y1': y1, 'y2': y2, 'x2': x2, 'y3': y3, 'y4': y4, 'ldate':ldate, 'ltime':ltime, 'volt':volt, 'curr':curr, 'powr':powr, 'lph':lph, 'runst':runst})


@login_required
def search(request):
	if request.method=="POST":

		Rid=request.POST['idno']
		try:
			sitedtls = BHSiteDetails.objects.get(CID_No=Rid)
		except BHSiteDetails.DoesNotExist:
			return HttpResponse('<h2>Invalid Claro ID</h2>')
		try:
			sitdata = DBData.objects.get(CID_No=Rid)
		except DBData.DoesNotExist:
			return HttpResponse('<h2>Invalid Claro ID</h2>')

		x1 = []
		y1 = []
		y2 = []

		chartdata = BHData.objects.filter(CID_No=Rid).exclude(DayEnergy=0)[:30]
		for x in chartdata:
			x1.append(str((x.Date).strftime('%d-%m-%Y')))
			y1.append(x.DayEnergy)
			y2.append(x.LPD)
		x1.reverse()
		y1.reverse()
		y2.reverse()

		if sitedtls.Capacity=='2HP DC':
			volt = 220
			ifact = 1
			vfact = 1
			lphfact = 6000
			minp=0.3 #minimum power
		else:
			volt = 584
			ifact = 2
			vfact = 2
			lphfact = 1700 #For 5HP
			minp=0.5

		gendate = date.today()
		now = datetime.now()
		ctime = now.strftime("%H:%M:%S")
		parts = ctime.split(":")
		ctVal = int(parts[0])*(60*60) + int(parts[1])*60 + int(parts[2])
		
		h1 = homeid.objects.get(CID_No=Rid)
		dt = random.randint(0, 5)
		# dt=0
		sTimes = random.randint(25200, 30600) #Morning Start time (Ex. 7AM = 7x60x60 = 25200)
		eTimes = random.randint(50400, 63000) #Evening End time

		k = 0

		if h1.Date:
			if h1.Date != gendate:
				h1 = homeid.objects.filter(CID_No=Rid).update(Status=1, Date=gendate, sTime=sTimes, eTime=eTimes, dtm=0, step=0)
				h1 = homeid.objects.get(CID_No=Rid)
		else:
			h1 = homeid.objects.filter(CID_No=Rid).update(Date=gendate, Status=dt, sTime=sTimes, eTime=eTimes, dtm=0, step=0)
			h1 = homeid.objects.get(CID_No=Rid)

		if h1.Status>0:
			stepTime = 0
			dTimeVal = h1.dtm+h1.sTime # data Receiving Time (in value)
			power = 0
			grossKwh = 0
			grosslpd0 = 0

			while dTimeVal<ctVal and dTimeVal<h1.eTime:
				dThr0 = dTimeVal/3600 #Time in Hours
				dTimeVal = dTimeVal+stepTime
				dTime = time.strftime('%H:%M:%S', time.gmtime(dTimeVal))
				dThr = dTimeVal/3600 #Time in Hours
				Irr = (0.282*pow(dThr,4)-13.52*pow(dThr,3)+203.9*pow(dThr,2)-1011*dThr+1274)*0.9711

				if Irr<0:
					Irr = 0

				temp = 25+(Irr-0)*(50-25)/739
				Tc = 25+(((temp-20)/0.8)*(Irr/1000))
				shadow = random.randint(75, 100)/100
				cloud = random.randint(0,5)

				if cloud<1:
					cloud = random.randint(30,50)/100
				else:
					cloud = 1

				pvolt = int((volt + math.log((Irr/1000), 2.72))*((1+(-0.3*(Tc-25)/100)))/vfact)*(random.randint(90, 120)/100) #PV Voltage
				pvi = (8.22*(Irr/1000))*((1+(0.05*(temp-25)/100)))*ifact*0.93*shadow*cloud #PV Current
									
				power0 = power
				power = pvolt*pvi/1000 #in kW

				energy = (dThr-dThr0)*(power+power0)/2
				grossKwh = grossKwh+energy
				lph = int(power*lphfact)
				if power<minp:
					lph = 0

				grosslpd = int((lphfact*(dThr-dThr0)*(power+power0)/2)+grosslpd0)
				grosslpd0 = grosslpd

				#timelist.append(dTime)
				stepTime = random.randint(600, 720)
				#stepTime = random.randint(1500, 1800)

				if sitedtls.Capacity=='5HP AC':
					freq = (15.795*power-(1.73161*power*power)+12.5331)*0.95	
					if power<minp:
						freq = 0
				else:
					freq = None

				now = datetime.now()
				ctime = now.strftime("%H:%M:%S")
				parts = ctime.split(":")
				ctVal = int(parts[0])*(60*60) + int(parts[1])*60 + int(parts[2])


				if ctVal>dTimeVal:
					k=k+1
					DataSet = BHInstData.objects.create(CID_No=Rid, Date=gendate, Time=dTime, Voltage=pvolt, Current=pvi, Power=power, Frequency=freq, Energy=energy, GrossEnergy=grossKwh, LPD=lph, GrossLPD=grosslpd, RunStatus=True)
					h1 = homeid.objects.filter(CID_No=Rid).update(dtm=dTimeVal, sTime=stepTime)
					h1 = homeid.objects.get(CID_No=Rid)
			# print(k)

			if k>9:
				dlt = k*0.12
				for i in range(int(dlt)):
					x=BHInstData.objects.filter(CID_No=Rid, Date=gendate)
					num = random.randint(1, len(x)-1)
					y = BHInstData.objects.filter(CID_No=Rid, Date=gendate)[num]
					# print(y)
					y.delete()
		x2 = []
		y3 = []
		y4 = []

		chartdata1 = BHInstData.objects.filter(CID_No=Rid, Date=date.today())
		for x in chartdata1:
			x2.append(str((x.Time).strftime('%H:%M')))
			y3.append((x.Power)*1000)
			y4.append(x.LPD)

		try:
			lv = BHInstData.objects.filter(CID_No=Rid, Date=date.today()).latest('Date', 'Time', 'Voltage', 'Current', 'LPD')
			ldate = lv.Date
			ltime = lv.Time
			volt = int(lv.Voltage)
			curr = lv.Current
			powr = lv.Power
			lph = int(lv.LPD)
			runst = lv.RunStatus
			if h1.eTime<ctVal:
				lv.RunStatus = False
				runst = lv.RunStatus
			if runst==True:
				runst = 'Running'
			else:
				runst = 'Currently Stopped'
		except BHInstData.DoesNotExist:
			ldate = ''
			ltime = ''
			volt = ''
			curr = ''
			powr = ''
			lph = ''
			runst = 'Not Running'
			return render(request, 'iddb.html', {'sitedtls':sitedtls, 'sitedata':sitdata, 'x1': x1, 'y1': y1, 'y2': y2, 'x2': x2, 'y3': y3, 'y4': y4, 'ldate':ldate, 'ltime':ltime, 'volt':volt, 'curr':curr, 'powr':powr, 'lph':lph, 'runst':runst})
		return render(request, 'iddb.html', {'sitedtls':sitedtls, 'sitedata':sitdata, 'x1': x1, 'y1': y1, 'y2': y2, 'x2': x2, 'y3': y3, 'y4': y4, 'ldate':ldate, 'ltime':ltime, 'volt':volt, 'curr':curr, 'powr':powr, 'lph':lph, 'runst':runst})



