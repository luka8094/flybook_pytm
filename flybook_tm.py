#!/usr/bin/env python3

from pytm.pytm import TM, Server, Data, Datastore, Dataflow, Boundary, Actor, Process, Lambda, ExternalEntity, Classification

tm = TM("Flybook webapp")
tm.description = "Flight booking service"
tm.isOrdered = True

#Boundary
Client_web = Boundary("Client/Web")
Web_app = Boundary("Web/Production")

#Actor
client = Actor("Client")
client.inBoundary = Client_web
client.protocol = "HTTPS"

'''
#Trust boundary
flybook_webapp = Server("Production")
flybook_webapp.OS = "Unix"
flybook_webapp.hasAccessControl = True
flybook_webapp.isHardened = False
'''

#Datastores
flybook_dbms = Datastore("MySQL Database (*)")
flybook_dbms.inBoundary = Web_app
flybook_dbms.isSQL = True
flybook_dbms.inScope = True
flybook_dbms.storesSensitiveData = True

#Processes
##Login
process_login = Process("Login")
process_login.inScope = True
process_login.inBoundary = Web_app

##Booking
process_flight_booking = Process("Flight booking")
process_flight_booking.inScope = True
process_flight_booking.inBoundary = Web_app

##Check service
process_check_service = Process("Service check")
process_check_service.inScope = True
process_check_service.inBoundary = Web_app

##Search flight
process_flight_search = Process("Flight search")
process_flight_search.inScope = True
process_flight_search.inBoundary = Web_app


login_data = Data(
	name="user login credentials (username, password)",
	classificaion=Classification.SENSITIVE,
	isPII=False,
	isCredentials=True,
	isStored=True,
	isSourceEncryptedAtRest=True,
	isDestEncryptedAtRest=True
)

search_data = Data(
	name="flight search query",
	classification=Classification.SENSITIVE,
	isPII=False,
	isCredentials=False,
	isStored=False,
	isSourceEncryptedAtRest=False,
	isDestEncryptedAtRest=False
)

flight_booking_data = Data(
	name="flight booking record",
	classification=Classification.SENSITIVE,
	isPII=False,
	isCredentials=False,
	isStored=True,
	isSourceEncryptedAtRest=True,
	isDestEncryptedAtRest=False
)

status_check = Data(
	name="billing logs",
	classification=Classification.SENSITIVE,
	isPII=False,
	isCredentials=False,
	isStored=True,
	isSourceEncryptedAtRest=True,
	isDestEncryptedAtRest=False
)

#Dataflows
##internal
client_to_flybook = Dataflow(client, process_login, "User credentials")
client_to_flybook.protocol = "HTTP"
client_to_flybook.dstPort = 8000
client_to_flybook.data = login_data

flybook_to_client = Dataflow(process_login, client, "Auth response")
flybook_to_client.protocol = "HTTP"
flybook_to_client.dstPort = 8000
flybook_to_client.data = login_data

client_to_flightbooking = Dataflow(client, process_flight_booking, "booking of flight")
client_to_flightbooking.protocol = "HTTP"
client_to_flightbooking.dstPort = 8000
client_to_flightbooking.data = search_data

flightbooking_to_client = Dataflow(process_flight_booking, client, "booking confirmation")
flightbooking_to_client.protocol = "HTTP"
flightbooking_to_client.dstPort = 8000
flightbooking_to_client.data = search_data

client_to_flightsearch = Dataflow(client, process_flight_search, "flight booking query")
client_to_flightsearch.protocol = "HTTP"
client_to_flightsearch.dstPort = 8000
client_to_flightsearch.data = search_data

flightsearch_to_client = Dataflow(client, process_flight_booking, "flight booking results")
flightsearch_to_client.protocol = "HTTP"
flightsearch_to_client.dstPort = 8000
flightsearch_to_client.data = search_data

flightsearch_to_servicecheck = Dataflow(process_flight_search, process_check_service, "retrieve webserver status")
flightsearch_to_servicecheck.protocol = "MySQL"
flightsearch_to_servicecheck.dstPort = 3306
flightsearch_to_servicecheck.data = status_check

flightbooking_to_servicecheck = Dataflow(process_flight_booking, process_check_service, "retrieve webserver status")
flightbooking_to_servicecheck.protocol = "MySQL"
flightbooking_to_servicecheck.dstPort = 3306
flightbooking_to_servicecheck.data = status_check

tm.process()
