from flask_restful import Resource


class HelloToHeroysWorld(Resource):
    def get(self):
        return {'Hello': ' there *twinkle'}, 200