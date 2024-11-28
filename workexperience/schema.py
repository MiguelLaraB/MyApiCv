import graphene
from graphene_django import DjangoObjectType
from .models import WorkExperience
from users.schema import UserType
from django.db.models import Q

class WorkExperienceType(DjangoObjectType):
    class Meta:
        model = WorkExperience

class Query(graphene.ObjectType):
    experiences = graphene.List(WorkExperienceType, search=graphene.String())
    experienceById = graphene.Field(WorkExperienceType, id_work_experience=graphene.Int())

    def resolve_experienceById(self, info, id_work_experience, **kwargs):
        user = info.context.user

        if user.is_anonymous:
            raise Exception('Not logged in')

        # Filtrar por ID y usuario
        return WorkExperience.objects.filter(posted_by=user, id=id_work_experience).first()

    def resolve_experiences(self, info, search=None, **kwargs):
        user = info.context.user

        if user.is_anonymous:
            raise Exception('Not logged in!')

        if search == "*":
            # Retorna las 10 primeras experiencias del usuario
            return WorkExperience.objects.filter(posted_by=user)[:10]

        # Filtrar por rol usando búsqueda parcial
        return WorkExperience.objects.filter(posted_by=user, role__icontains=search)


class CreateWorkExperience(graphene.Mutation):
    id_work_experience = graphene.Int()
    role               = graphene.String()
    company            = graphene.String()
    accomplishments    = graphene.List(graphene.String)
    start_date         = graphene.Date()
    end_date           = graphene.Date()
    location           = graphene.String()
    posted_by          = graphene.Field(UserType)

    class Arguments:
        role            = graphene.String(required=True)
        company         = graphene.String(required=True)
        accomplishments = graphene.List(graphene.String, required=False)
        start_date      = graphene.Date(required=True)
        end_date        = graphene.Date(required=False)
        location        = graphene.String(required=True)

    def mutate(self, info, role, company, start_date, location, accomplishments=None, end_date=None):
        user = info.context.user

        if user.is_anonymous:
            raise Exception('Not logged in!')

        # Crear una nueva instancia de WorkExperience
        work_experience = WorkExperience(
            role=role,
            company=company,
            accomplishments=accomplishments or [],
            start_date=start_date,
            end_date=end_date,
            location=location,
            posted_by=user
        )
        work_experience.save()

        return CreateWorkExperience(
            id_work_experience=work_experience.id,
            role=work_experience.role,
            company=work_experience.company,
            accomplishments=work_experience.accomplishments,
            start_date=work_experience.start_date,
            end_date=work_experience.end_date,
            location=work_experience.location,
            posted_by=work_experience.posted_by
        )


class DeleteWorkExperience(graphene.Mutation):
    id_work_experience = graphene.Int()

    class Arguments:
        id_work_experience = graphene.Int()

    def mutate(self, info, id_work_experience):
        user = info.context.user

        if user.is_anonymous:
            raise Exception('Not logged in!')

        # Buscar experiencia laboral
        current_work_experience = WorkExperience.objects.filter(posted_by=user, id=id_work_experience).first()

        if not current_work_experience:
            raise Exception('Invalid Work Experience ID!')

        # Eliminar la experiencia
        current_work_experience.delete()

        return DeleteWorkExperience(id_work_experience=id_work_experience)


class Mutation(graphene.ObjectType):
    create_work_experience = CreateWorkExperience.Field()
    delete_work_experience = DeleteWorkExperience.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
