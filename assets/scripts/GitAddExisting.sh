#!/bin/bash
#$1 - directory project
#$2 - User NAme
#$3 - repo name
cd  $1
echo $PWD

remoteRepo='git@github.com:'$2'/'$3'.git'
echo $remoteRepo


response=$(curl --write-out %{http_code} --silent --output /dev/null -u $2 https://api.github.com/user/repos -d '{"name":"'$3'"}')

if [ "$response" != "200" ]
then
     echo "git request failed with: "$response" you probably have 2FA"
fi

git init
git add .
git commit -m "First Commit"
git remote add origin $remoteRepo 
git push -u origin master
