import graphene
from api.schema import Query as ApiQuery, Mutation as ApiMutation

class Query(ApiQuery, graphene.ObjectType):
    pass

class Mutation(ApiMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
