README
======

What is Blumber?
-----------------

Blumber is a very simple blogger extension that can be added to your website in a few seconds. It is a bunch of div elements which are automatically built using AngularJS and python. All you need to do for writing a new post on your blog is to run a simple python command on terminal and everything else's being taken care of by Blumber.

Installation
------------

Follow these steps to add Blumber to your page:  
	1. First include jQuery and AngularJS in the header of your html document:  
  
  
```  
		<script src="//code.jquery.com/jquery-1.10.2.min.js"></script>  
		<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular.min.js"></script>  



	   Notice that these are the most recent versions at the time I wrote this README file. You may want to use later versions by the time you use this project (Assuming they are backward compatible!).  
	
	2. Next, place the following HTML code into your html document:  
  	
  
```  
		<div ng-show="items.length">  
			<h4><small>RECENT POSTS</small></h4>    
			<div ng-repeat="item in items | reverse">  
				<ng-include src="item"></ng-include>  
			</div>  
		</div>  



	   I didn't include my styles for this element because you may want to have it styled in a way that fits your website's design and that can be done simply by adding some CSS.  
	  
	3. Copy and paste the following script somewhere in your HTML document or wherever you're having your scripts on.  

```
		<script>  
		var app = angular.module("myApp", []);  
		app.controller("myCtrl", function($scope,$http) {  
		  $http.get('posts.json')  
		            .success(function(data) {   
		            	  $scope.items = data; 
		            })  
		            .error(function() {  
		                defer.reject('could not find posts.json');  
		            });  
		});  
		app.filter('reverse', function() {  
		  return function(items) {  
		    return items.slice().reverse();  
		  };  
		});  
		</script>     

	4. Since this project uses SCP to send/receive files, you must have your DSA key in order to make a connection to the server.  
	5. Finally you must have your SSH credential in a JSON file named auth.json which is in the same directory as main.py file. The contents of auth.json must look like this:  
		{"username":"your_username","password":"your_password","hostname":"your_hostname","port":"port_number","key_path":"path_to_DSA_key"}  
	6. There's not any step 6, done. It's as simple as it sounds!  
  
Writing a post
--------------
  
In order to write a post open command line and go to the directory where main.py is. Type the following command to run the python script:  
	  
	python main.py  
  
it will open a temporary file using vi editor with the following contents:  
  
	################THIS PART WILL BE IGNORED##################
	Fill out each section with relevant information about your post.
	 - Separate multiple tags with ',' character.
	 - In order to include a code snippet use <pre></pre> tag (feel free to use other HTML phrase elements).
	 - Do not make any changes to above lines.
	###########################################################
	-------------TITLE--------------

	-------------TAGS---------------

	-------------BODY---------------

just fill the title, tags, and body parts following the given instructions and then close vi. It will automatically upload the post to your server. Once uploaded open your webpage and reload it, you should be able to see the post.  
[vi editor basic commands][1]
Documentation
-------------
  
I tried to put a reasonable amount of comments when I wrote this so if in any case you wanted to change anything take a quick look at my comments then you should be able to figure out what's going on and what I have done (It's not rocket science, it's ridiculously simple!).  
  

[1]: https://www.cs.colostate.edu/helpdocs/vi.html