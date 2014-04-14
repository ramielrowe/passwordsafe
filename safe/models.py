import bcrypt
from Crypto.Cipher import AES
from Crypto import Random
from django.db import models

from passwordsafe import settings
from safe import exceptions


class User(models.Model):
    username = models.TextField(max_length=100)
    password = models.BinaryField(max_length=5000)

    @staticmethod
    def create(username, raw_password):
        if User.objects.filter(username=username).count() == 0:
            salt = bcrypt.gensalt(settings.USER_PASSWORD_ROUNDS)
            password = bcrypt.hashpw(bytes(str(raw_password)), salt)
            user = User(username=username,
                        password=password)
            user.save()
            return user
        else:
            raise exceptions.UserAlreadyExists()

    @staticmethod
    def authenticate(username, raw_password):
        try:
            user = User.objects.get(username=username)
            password = bytes(user.password)
            if password == bcrypt.hashpw(bytes(str(raw_password)), password):
                return user
        except User.DoesNotExist:
            pass


class Password(models.Model):
    user = models.ForeignKey(User, related_name='passwords')
    name = models.CharField(max_length=200)
    password = models.BinaryField(max_length=5000)
    iv = models.BinaryField(max_length=5000)

    @staticmethod
    def get_user_password_names(user_id):
        return [value['name'] for value in
                Password.objects.filter(user_id=user_id).values("name")]

    @staticmethod
    def create(user_id, name, raw_password, key):
        if Password.objects.filter(user_id=user_id, name=name).count() > 0:
            raise exceptions.PasswordAlreadyExists()
        iv = Random.new().read(AES.block_size)
        key = str(key) + ('0' * (32 - len(key)))
        aes = AES.new(bytes(key), AES.MODE_CFB, iv)
        password = aes.encrypt(bytes(str(raw_password)))
        pass_obj = Password(user_id=user_id, name=name,
                            password=password, iv=iv)
        pass_obj.save()
        return pass_obj

    @staticmethod
    def get_password(user_id, name, key):
        pass_obj = Password.objects.get(user_id=user_id, name=name)
        key = str(key) + ('0' * (32 - len(key)))
        aes = AES.new(bytes(key), AES.MODE_CFB, pass_obj.iv)
        password = aes.decrypt(pass_obj.password)
        return password

    @staticmethod
    def delete_password(user_id, name):
        Password.objects.get(user_id=user_id, name=name).delete()
