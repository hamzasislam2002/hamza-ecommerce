from project import mail

def test_get_registration(test_client):

	response = test_client.get('/users/register')
	assert b'User Registration' in response.data
	assert b'Email' in response.data
	assert b'Password' in response.data
	
def test_registration_valid(test_client):
	with mail.record_messages() as outbox:
		response = test_client.post('/users/register',
								data={'email': 'hamza@curry.com',
									'password': 'hehe123'},
									follow_redirects=True)
		assert response.status_code == 200
		assert b'Thanks for registering, hamza@curry.com' in response.data
		assert len(outbox) == 1
		assert outbox[0].sender == 'hamzaecommerce@gmail.com'
		assert outbox[0].recipients[0] == 'hamza@curry.com'
		assert 'http://localhost/users/confirm/' in outbox[0].html

def test_confirm_email_valid(test_client):
	confirm_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
	token = confirm_serializer.dumps('patrick@gmail.com', salt='email-confirmation-salt')

	response = test_client.get('/users/confirm/'+token, follow_redirects=True)
	
	assert response.status_code == 200
	assert b'Account already confirmed.' in response.data
	query = database.select(User).where(User.email == 'hamza@curry.com')


def test_registration_invalid(test_client):
	response = test_client.post('/users/register',
							 data={'email': 'hamza@curry.com',
			                       'password': ''},
								   follow_redirects=True)
	assert response.status_code == 200
	assert b'Thanks for registering, hamza@curry.com' not in response.data
	assert b'[This field is required.]' in response.data
	
def test_registration_identical(test_client):
	test_client.post('/users/register',
							 data={'email': 'hamza@curry.com',
			                       'password': 'hehe123'},
								   follow_redirects=True)
	response = test_client.post('/users/register',
							 data={'email': 'hamza@curry.com',
			                       'password': 'hehe1234'},
								   follow_redirects=True)
	assert response.status_code == 200
	assert b'Thanks for registering, hamza@curry.com' not in response.data
	assert b'ERROR! Email (hamza@curry.com) already exists.' in response.data

def test_get_login_page(test_client):
	response = test_client.get('/users/login')
	assert response.status_code == 200
	assert b'Login' in response.data
	assert b'Email' in response.data
	assert b'Password' in response.data
	assert b'Login' in response.data

def test_valid_login_and_logout(test_client, register_default_user):
	response = test_client.post('/users/login',
							 data={'email': 'hamza@curry.com',
			  					   'password': 'hehe123'},
								   follow_redirects=True)
	assert response.status_code == 200
	assert b'Thanks for logging in, hamza@curry.com!' in response.data
	assert b'Please log in to access this page.' not in response.data

	response = test_client.get('/users/logout', follow_redirects=True)
	assert response.status_code == 200
	assert b'Goodbye!' in response.data
	assert b'Please log in to access this page.' not in response.data

def test_invalid_login(test_client, register_default_user):
	response = test_client.post('/users/login',
							 	data={'email': 'hamza@curry.com',
			   						  'password': 'hehe12345'},
									  follow_redirects=True)
	assert response.status_code == 200
	assert b'ERROR! Incorrect login credentials.' in response.data

def test_valid_already_logged_in(test_client, log_in_default_user):
	response = test_client.post('/users/login',
							 	data={'email': 'hamza@curry.com',
			   						'password': 'hehe123'},
									follow_redirects=True)
	assert response.status_code == 200
	assert b'Already logged in!' in response.data

def test_invalid_logout(test_client):
	response = test_client.post('/users/logout', follow_redirects=True)
	assert b'Goodbye!' not in response.data
	assert b'Method Not Allowed' in response.data

def test_invalid_logout_not_logged_in(test_client):
	test_client.get('/users/logout', follow_redirects=True)
	response = test_client.get('/users/logout', follow_redirects=True)
	assert b'Goodbye!' not in response.data
	assert b'Login' in response.data
	assert b'Please log in to access this page.' in response.data

def test_user_profile_logged_in(test_client, log_in_default_user):
	response = test_client.get('/users/profile')
	assert response.status_code == 200
	assert b'User Profile' in response.data
	assert b'Email: hamza@curry.com' in response.data

def test_user_profile_not_logged_in(test_client):
	response = test_client.get('/users/profile', follow_redirects=True)
	assert response.status_code == 200
	assert b'User Profile!' not in response.data
	assert b'Email: hamza@curry.com' not in response.data
	assert b'Please log in to access this page.' in response.data

def navigation_bar_logged_in(test_client, log_in_default_user):
	response = test_client.get('/')
	assert response.status_code == 200
	assert b'Profile' in response.data
	assert b'Logout' in response.data
	assert b'Register' not in response.data
	assert b'Login' not in response.data

def navigation_bar_not_logged_in(test_client):
	response = test_client.get('/')
	assert b'Profile' not in response.data
	assert b'Login' not in response.data

def test_login_valid_path(test_client, register_default_user):
	response = test_client.post('users/login?next=%2Fusers%2Fprofile',
							 	data={'email': 'hamza@curry.com',
			   						  'password': 'hehe123'},
									  follow_redirects=True)
	assert response.status_code == 200
	assert b'User Profile' in response.data
	assert b'Email: hamza@curry.com' in response.data

	test_client.get('/users/logout', follow_redirects=True)

def test_login_next_invalid_path(test_client, register_default_user):
	response = test_client.post('users/login?next=http://www.badsite.com',
							 	data={'email': 'hamza@curry.com',
			   						  'password': 'hehe123'},
									  follow_redirects=True)
	assert response.status_code == 200
	assert b'User Profile' not in response.data
	assert b'Email: hamza@curry.com' not in response.data


# def test_get_resend_email_confirmation_logged_in(test_client, log_in_default_user):
# 	with mail.record_messages() as outbox:
# 		response = test_client.get('/users/resend_email_confirmation', follow_redirects=True)
# 		assert response.status_code == 200
# 		assert b'Email sent to confirm your email address. Please check your email' in response.data
# 		assert len(outbox) == 1
# 		assert outbox[0].subject == 'Confirm Your Email Address'
# 		assert outbox[0].sender == 'hamzaecommerce@gmail.com'
# 		assert outbox[0].recipients[0] == 'hamza@curry.com'
# 		assert 'http://localhost/users/confirm/' in outbox[0].html

# def test_get_resend_email_confirmation_not_logged_in(test_client):
# 	with mail.record_messages() as outbox:
# 		response = test_client.get('/users/resend_email_confirmation', follow_redirects=True)
# 		assert response.status_code == 200
# 		assert b'Email sent to confirm your email address. Please check your email!' not in response.data
# 		assert len(outbox) == 0
# 		assert b'Please log in to access this page.' in response.data



# def test_get_change_password_logged_in(test_client, log_in_default_user):
