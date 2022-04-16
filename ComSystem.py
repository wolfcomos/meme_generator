class User():
    def __init__(self, username, password,score=0,numLikes=0):
        self.username = username
        self.password = password
        self.score = score
        self.numLikes = numLikes

    def getUsername(self):
        return self.username
    def getScore(self):
        return self.score
    def getPassword(self):
        return self.password
    def getNumLikes(self):
        return self.numLikes
    def post(self,post):
        print(post)
    def addComment(self,comment):
        print(comment)
        self.score += 10
    def giveLike(self,user):
        # 点赞功能
        user.numLikes += 1
        self.score += 1