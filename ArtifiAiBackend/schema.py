import graphene
from styletransfer.schema import Query, Mutation

schema = graphene.Schema(query=Query, mutation=Mutation)
