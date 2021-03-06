#!/usr/bin/python3
import os
import gevent.monkey
gevent.monkey.patch_all()
import tornado.web, tornado.wsgi, uimodules
import handlers, persistence
import config
import caching

settings = {
	'debug': config.getDebug(), 
	'template_path': "views", 
	'static_path': 'static',
	'ui_modules': uimodules,
	'cookie_secret': config.getSecrete(),
	"login_url": "/login",
	"xsrf_cookies": True
}
application = tornado.wsgi.WSGIApplication([
	(r"/", handlers.MainHandler),
	(r"/login", handlers.LoginFormHandler),
	(r"/authorization", handlers.AuthorizationHandler),
	(r"/signup", handlers.SignUpFormHandler),
	(r"/users", handlers.UserHandler),
	(r"/logout", handlers.LogoutHandler),
	(r"/notebook", handlers.NotebookHandler),
	(r"/notebook/collections", handlers.CollectionsHandler),
	(r"/notebook/collections/manage", handlers.ManageCollectionsHandler),
	(r"/notebook/collections/new_form", handlers.NewCollectionHandler),
	(r"/notebook/collections/([0-9a-zA-Z\-_%]+)", handlers.CollectionHandler),
	(r"/notebook/collections/([0-9a-zA-Z\-_%]+)/new_form", handlers.NewListHandler),
	(r"/notebook/collections/([0-9a-zA-Z\-_%]+)/manage", handlers.ListsManageHandler),
	(r"/notebook/collections/([0-9a-zA-Z\-_%]+)/list([0-9]+)", handlers.ListsHandler),
	(r"/notebook/review/", handlers.ReviewListHandler),
	(r"/notebook/review", handlers.ReviewHandler),
	(r"/notebook/definition/([0-9a-zA-Z\-_%]+)", handlers.DefHandler),
	(r"/static/(.+)", tornado.web.StaticFileHandler)
], **settings)
db = persistence.Persistence()
raw_db = db.getUnderlyingDb()
application.db = db
application.wordCache = caching.WordCache(raw_db)
def start_server(server, process_count):
	import multiprocessing
	server.start()
	for i in range(process_count - 1):
		multiprocessing.Process(target=server.serve_forever, args=tuple()).start()
	server.serve_forever()

if __name__ == "__main__":
	from socketio.server import SocketIOServer
	import socket
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		os.unlink('/tmp/wordtool.socket')
	except OSError:
		pass
	s.bind('/tmp/wordtool.socket')
	s.listen(10000)
	server = SocketIOServer(s, application, policy_server = False)
	start_server(server, 3)
