# apps/user/serializers.py
from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from datetime import date
from apps.users.models import User
from apps.users.exceptions import CustomValidationError
from django.contrib.auth.models import update_last_login

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    password_check = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password_check', 'gender', 'birth_date']

    def validate(self, attrs):
        """
        회원가입 데이터 검증
        - 이메일 중복 체크
        - 비밀번호/비밀번호 확인 일치여부 검증
        """
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': '이미 존재하는 이메일입니다.'})

        if attrs['password'] != attrs['password_check']:
            raise serializers.ValidationError({'password': '비밀번호와 비밀번호 확인이 일치하지 않습니다.'})

        attrs['created_at'] = date.today()

        return attrs

    def create(self, validated_data):
        """ validated_data를 받아 유저를 생성한 후 토큰을 반환합니다. """
        password = validated_data.get('password')
        # 유저 생성
        user = User(
            email=validated_data['email'],
            password=password,
            name=validated_data['name'],
            gender=validated_data['gender'],
            birth_date=validated_data['birth_date'],
        )

        user.set_password(password)
        user.save()
        return user


class SignInSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        user = authenticate(**data)
        if user:
            update_last_login(None, user)
            token = TokenObtainPairSerializer.get_token(user)
            refresh = str(token)
            access = str(token.access_token)

            data = {
                'user': user.email,
                'refresh': refresh,
                'access': access,
            }

            return data

        raise CustomValidationError({"detail": "No active account found with the given credentials"}, 'username', status_code=status.HTTP_401_UNAUTHORIZED)

class SignOutSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

    def validate(self, data, **kwargs):
        self.access = data["access"]
        self.refresh = data["refresh"]
        return data

    # serializer.save()에 실행되는 메소드
    def save(self, **kwargs): 
        try:
            RefreshToken(self.refresh).blacklist() # validate에서 받아온 refresh 토큰 블랙리스트 등록
        except TokenError:
            raise serializers.ValidationError(detail={"InvalidError": "Token is invalid or expired."})


class UserSerializer(serializers.ModelSerializer):
    class Meta:
          model = User
          fields = '__all__'
