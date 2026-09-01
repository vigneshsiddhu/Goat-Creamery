from .models import BusinessUser


class CurrentBusinessMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # =====================================================
        # DEFAULT VALUES
        # =====================================================
        request.business = None
        request.business_user = None
        request.business_role = None

        # =====================================================
        # AUTHENTICATED USER
        # =====================================================

        if request.user.is_authenticated:

            business_user = (
                request.user.business_users
                .select_related("business")
                .filter(
                    is_active=True,
                    business__status=True
                )
                .first()
            )

            if business_user:

                # Current BusinessUser
                request.business_user = business_user

                # Current Business
                request.business = business_user.business

                # Current Role
                request.business_role = business_user.role


        # =====================================================
        # CONTINUE REQUEST
        # =====================================================

        response = self.get_response(request)

        return response