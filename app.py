from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import requests
import json
import re
app = Flask(__name__)
service = Api(app)

access_token = 'use access token here'
base_url = 'https://api.github.com/'

class ProjectCollaborator(Resource):

	''' add or delete project collaborators'''
	
	def put(self):
	
		''' add user in project'''
		
		request_body = request.get_json()
		project_id = request_body['project_id']
		username = request_body['username']
		url = base_url + 'projects/' + project_id +'/collaborators/' + username
		return self.make_call(request.method, url)

	def delete(self): 
	
		''' delete user from the project'''
		
		request_body = request.get_json()
		project_id = request_body['project_id']
		username = request_body['username']
		url = base_url + 'projects/' + project_id +'/collaborators/' + username
		return self.make_call(request.method, url)
        
	def make_call(self, method_name, url):
	
		''' call the github api '''
		
		payload = {
			'permission': 'read'
		}
		headers = {
			'Authorization': 'token %s' % access_token,
			'Accept': 'application/vnd.github.inertia-preview+json'
		}
		if method_name == 'DELETE':
			try: 
				res = requests.delete(url, data= json.dumps(payload), headers=headers )
			except Exception as e:
				return jsonify({'success':'false',
								'message':str(e)})
		elif method_name == 'PUT':
			try:
				res = requests.put(url, data= json.dumps(payload), headers=headers)
			except Exception as e:
				return jsonify({'success':'false',
								'message':str(e)})
		else:
			pass

		return jsonify({'success': 'false' if (r.status_code >= 400) else 'true',
						'message':res.text})

class Project(Resource):
	
	''' create the project '''
	
	def get(self):
	
		''' get project list associated with org '''
		
		org_name = request.args.get('org')
		projects = self.fetch_projects(org_name)
		return jsonify({'success': 'true',
						'message': projects})

	def post(self):
	
		''' create the project '''
		
		request_body = request.get_json()
		org = request_body['org']
		project_name = request_body['project_name']
		desc = request_body['description']
		url = base_url + 'orgs/' + org + '/projects'
		payload = {
			'name': project_name,
			'description': desc
		}
		headers = {
			'Authorization': 'token %s' % access_token,
			'Accept': 'application/vnd.github.inertia-preview+json'
		}
		project_list = json.loads(self.fetch_projects(org))
		for project in project_list:
			if project_name == project['name']:
				return jsonify({'success':'false',
								'message':'project already exist'})
		try:
			res = requests.post(url, data=json.dumps(payload), headers=headers)
		except Exception as e:
			return jsonify({'success':'false',
							'message':str(e)})
		
		return jsonify({'success':'true',
						'message':res.text})        

	def fetch_projects(self, org):
	
		''' fetch all the created project '''
		
		url = base_url + 'orgs/' + org + '/projects'

		payload = {
			'state': 'all'
		}
		headers = {
			'Authorization': 'token %s' % access_token,
			'Accept': 'application/vnd.github.inertia-preview+json'
		}
		try:
			res = requests.get(url,
							params=payload, headers = headers)
		except Exception as e:
			return []
		return res.text

class Team(Resource):
	
	def post(self):
		
		''' creates the team '''
		
		request_body = request.get_json()
		try:
			team_name = request_body['name']
			org_name = request_body['org_name']
			payload = {'name': team_name}
			headers = {'Authorization':'token %s' % access_token}
			url = base_url + 'orgs/' + org_name + '/teams'
			r = requests.post(url,
							data=json.dumps(payload), headers=headers)
		except Exception as e:
			return jsonify({'success':'false',
							'message':str(e)})
		res = json.loads(r.text)
		try:
			res['errors']
			return jsonify({'success':'false',
							'message':res['errors'][0]['message']})
		except KeyError:
			pass
	
		return jsonify({'success':'true',
						'message':r.text})


	
service.add_resource(Team,'/team')
service.add_resource(Project,'/project')
service.add_resource(ProjectCollaborator, '/collaborators/proj')

if __name__ == '__main__':
	app.run(debug = True)