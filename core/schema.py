import graphene
from api.schema import Query as ApiQuery, Mutation as ApiMutation, Subscription as ApiSubscription

class Query(ApiQuery, graphene.ObjectType):
    pass

class Mutation(ApiMutation, graphene.ObjectType):
    pass

class Subscription(ApiSubscription, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)

