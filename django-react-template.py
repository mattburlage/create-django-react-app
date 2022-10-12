# This script creates a default Django backed React App
#
# Author: mattburlage (github.com/mattburlage)
#
# This is based largely on the following walkthrough:
# https://medium.com/@dakota.lillie/django-react-jwt-authentication-5015ee00ef9a

import sys
import os

try:
    project_name = sys.argv[1]
except IndexError:
    print("What is the desired name of the project?")
    project_name = input()

try:
    import django
except ModuleNotFoundError as e:
    print(e)
    os.system('pip install django')
    os.system('cls')
    
try:
    import pipenv
except ModuleNotFoundError as e:
    print(e)
    os.system('pip install pipenv')
    os.system('cls')

# Build Django and React apps
os.system(f"django-admin startproject {project_name}")
os.chdir(project_name)
os.system(f"python manage.py startapp api")
os.system('npx create-react-app app')

# Install Django REST Framework and other packages
os.system('pipenv install')
os.system('pipenv install django')
os.system('pipenv install djangorestframework')
os.system('pipenv install djangorestframework-jwt')
os.system('pipenv install django-cors-headers')
os.system('pipenv run python manage.py migrate')

project_dir = f"{os.getcwd()}\\{project_name}"

def write_file(file, write_type, text):
    f = open(file, write_type)
    f.write(text)
    f.close


# Write to settings file
new_settings = """
# JWT Settings
INSTALLED_APPS += [
    'api.apps.ApiConfig',
    'rest_framework',
    'corsheaders',
]

NEW_MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"]
MIDDLEWARE = NEW_MIDDLEWARE + MIDDLEWARE

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
)

JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER': '""" + project_name + """.jwt_utils.my_jwt_response_handler'
}
"""
write_file(f"{project_dir}\\settings.py", 'a+', new_settings)


# Write URLs file

new_urls = """
# JWT URLs
from rest_framework_jwt.views import obtain_jwt_token
from django.urls import path, include

urlpatterns += [
    path('token-auth/', obtain_jwt_token),
    path('api/', include('api.urls'))
]
"""
write_file(f"{project_dir}\\urls.py", 'a+', new_urls)


# Crete serializers file
serializer_text = """
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username',)


class UserSerializerWithToken(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('token', 'username', 'password')
"""
write_file(f"{os.getcwd()}\\api\\serializers.py", 'w+', serializer_text)


# Write API views file
f = open(f"{os.getcwd()}\\api\\views.py", "w+")
views_text = """
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, UserSerializerWithToken


@api_view(['GET'])
def current_user(request):
    
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserList(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
f.write(views_text)
f.close()

# Create app URLs file
f = open(f"{os.getcwd()}\\api\\urls.py", "w+")
app_urls_text = """
from django.urls import path
from .views import current_user, UserList

urlpatterns = [
    path('current_user/', current_user),
    path('users/', UserList.as_view())
]
"""
f.write(app_urls_text)
f.close()

# Create jwt_utils file
f = open(f"{project_dir}\\jwt_utils.py", "w+")
app_urls_text = """
from api.serializers import UserSerializer

def my_jwt_response_handler(token, user=None, request=None, extras=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }
"""
f.write(app_urls_text)
f.close()


# Set up React front end
os.chdir('app')
os.system('npm i prop-types -S')

os.mkdir('src/components')

nav_js_file = """
import React from 'react';
import PropTypes from 'prop-types';

function Nav(props) {
  const logged_out_nav = (
    <ul>
      <li onClick={() => props.display_form('login')}>login</li>
      <li onClick={() => props.display_form('signup')}>signup</li>
    </ul>
  );

  const logged_in_nav = (
    <ul>
      <li onClick={props.handle_logout}>logout</li>
    </ul>
  );
  return <div>{props.logged_in ? logged_in_nav : logged_out_nav}</div>;
}

export default Nav;

Nav.propTypes = {
  logged_in: PropTypes.bool.isRequired,
  display_form: PropTypes.func.isRequired,
  handle_logout: PropTypes.func.isRequired
};
"""
write_file(f"{os.getcwd()}\\src\\components\\Nav.js", 'w+', nav_js_file)

login_form_text = """
import React from 'react';
import PropTypes from 'prop-types';

class LoginForm extends React.Component {
  state = {
    username: '',
    password: ''
  };

  handle_change = e => {
    const name = e.target.name;
    const value = e.target.value;
    this.setState(prevstate => {
      const newState = { ...prevstate };
      newState[name] = value;
      return newState;
    });
  };

  render() {
    return (
      <form onSubmit={e => this.props.handle_login(e, this.state)}>
        <h4>Log In</h4>
        <label htmlFor="username">Username</label>
        <input
          type="text"
          name="username"
          value={this.state.username}
          onChange={this.handle_change}
        />
        <label htmlFor="password">Password</label>
        <input
          type="password"
          name="password"
          value={this.state.password}
          onChange={this.handle_change}
        />
        <input type="submit" />
      </form>
    );
  }
}

export default LoginForm;

LoginForm.propTypes = {
  handle_login: PropTypes.func.isRequired
};
"""
write_file(f"{os.getcwd()}\\src\\components\\LoginForm.js", 'w+', login_form_text)

signup_form_text = """
import React from 'react';
import PropTypes from 'prop-types';

class SignupForm extends React.Component {
  state = {
    username: '',
    password: ''
  };

  handle_change = e => {
    const name = e.target.name;
    const value = e.target.value;
    this.setState(prevstate => {
      const newState = { ...prevstate };
      newState[name] = value;
      return newState;
    });
  };

  render() {
    return (
      <form onSubmit={e => this.props.handle_signup(e, this.state)}>
        <h4>Sign Up</h4>
        <label htmlFor="username">Username</label>
        <input
          type="text"
          name="username"
          value={this.state.username}
          onChange={this.handle_change}
        />
        <label htmlFor="password">Password</label>
        <input
          type="password"
          name="password"
          value={this.state.password}
          onChange={this.handle_change}
        />
        <input type="submit" />
      </form>
    );
  }
}

export default SignupForm;

SignupForm.propTypes = {
  handle_signup: PropTypes.func.isRequired
};
"""
write_file(f"{os.getcwd()}\\src\\components\\SignupForm.js", 'w+', signup_form_text)

app_js_text = """
import React, { Component } from 'react';
import Nav from './components/Nav';
import LoginForm from './components/LoginForm';
import SignupForm from './components/SignupForm';
import './App.css';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      displayed_form: '',
      logged_in: localStorage.getItem('token') ? true : false,
      username: ''
    };
  }

  componentDidMount() {
    if (this.state.logged_in) {
      fetch('http://localhost:8000/api/current_user/', {
        headers: {
          Authorization: `JWT ${localStorage.getItem('token')}`
        }
      })
        .then(res => res.json())
        .then(json => {
          this.setState({ username: json.username });
        });
    }
  }

  handle_login = (e, data) => {
    e.preventDefault();
    fetch('http://localhost:8000/token-auth/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
      .then(res => res.json())
      .then(json => {
        localStorage.setItem('token', json.token);
        this.setState({
          logged_in: true,
          displayed_form: '',
          username: json.user.username
        });
      });
  };

  handle_signup = (e, data) => {
    e.preventDefault();
    fetch('http://localhost:8000/api/users/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
      .then(res => res.json())
      .then(json => {
        localStorage.setItem('token', json.token);
        this.setState({
          logged_in: true,
          displayed_form: '',
          username: json.username
        });
      });
  };

  handle_logout = () => {
    localStorage.removeItem('token');
    this.setState({ logged_in: false, username: '' });
  };

  display_form = form => {
    this.setState({
      displayed_form: form
    });
  };

  render() {
    let form;
    switch (this.state.displayed_form) {
      case 'login':
        form = <LoginForm handle_login={this.handle_login} />;
        break;
      case 'signup':
        form = <SignupForm handle_signup={this.handle_signup} />;
        break;
      default:
        form = null;
    }

    return (
      <div className="App">
        <Nav
          logged_in={this.state.logged_in}
          display_form={this.display_form}
          handle_logout={this.handle_logout}
        />
        {form}
        <h3>
          {this.state.logged_in
            ? `Hello, ${this.state.username}`
            : 'Please Log In'}
        </h3>
      </div>
    );
  }
}

export default App;
"""
write_file(f"{os.getcwd()}\\src\\App.js", 'w+', app_js_text)

# Write App.css
app_css_text = """
.App {
  margin-left: 20px;
}

input {
  display: block;
  margin: 5px 0 5px;
}
"""
write_file(f"{os.getcwd()}\\src\\App.css", 'w+', app_css_text)
