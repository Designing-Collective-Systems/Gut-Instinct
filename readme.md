# 0)  Optional – code editor
#     VS Code is a great choice.

# 1)  Meteor CLI (1.6.1.4 exactly – the version the repo was built on)
curl https://install.meteor.com/ | sh
#     (If you already have Meteor ≥2.x installed system‑wide, use a tool
#      like asdf or nvm to isolate versions, then run the script.)


# 2) Install Required Packages
meteor npm install

# 3)  Run the app
meteor
# → open http://localhost:3000  in your browser
