# 0)  Optional – code editor
#     VS Code is a great choice.

# 1)  Meteor CLI (1.6.1.4 exactly – the version the repo was built on)
curl https://install.meteor.com/?release=1.6.1.4 | sh
#     (If you already have Meteor ≥2.x installed system‑wide, use a tool
#      like asdf or nvm to isolate versions, then run the script.)

# 2)  Clone the repo & move into it
git clone <your‑fork‑url> gut‑instinct
cd gut‑instinct

# 3)  Install Node packages that Meteor does **not** manage itself
meteor npm install \
  normalize-strings \
  util \
  stream-browserify \
  path-browserify \
  @babel/runtime \
  @observablehq/plot \
  compromise@12.4.0 \      # ← ES5 build; avoids “import outside module”
  elasticlunr \
  meteor-node-stubs \
  sass \
  bourbon

# 4)  Add required Meteor packages
meteor add \
  reactive-dict \
  session \
  blaze \
  accounts-base \
  accounts-password \
  http

# 5) go to server/compile-scss.server.js
go to line 10 and change the path according to your system

# 5)  One‑time project initialisation
meteor reset        # wipes the local DB / build cache
meteor update       # brings every Meteor package to 1.6.1.x line

# 6)  SCSS → CSS
#     The file lives at  server/compile-scss.server.js
#     and runs automatically on every `meteor` start,
#     but you can trigger it manually if you change styles:
node server/compile-scss.server.js
#     (If you kept the old standalone script, use: `node compile-scss.js`)

# 7)  Run the app
meteor
# → open http://localhost:3000  in your browser
