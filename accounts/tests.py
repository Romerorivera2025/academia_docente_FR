from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountsAuthTests(TestCase):
    """Pruebas de registro, inicio de sesión, panel protegido y cierre de sesión."""

    def test_registro_valido(self):
        response = self.client.post(
            reverse('accounts:registro'),
            {
                'username': 'docente_demo',
                'password1': 'ClaveSegura2026!',
                'password2': 'ClaveSegura2026!',
            },
        )
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertTrue(User.objects.filter(username='docente_demo').exists())

    def test_registro_contrasenas_distintas_no_crea_cuenta(self):
        response = self.client.post(
            reverse('accounts:registro'),
            {
                'username': 'docente_fallido',
                'password1': 'ClaveSegura2026!',
                'password2': 'ClaveDiferente2026!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('password2', response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='docente_fallido').exists())

    def test_visita_anonima_al_panel_redirige_a_login(self):
        panel_url = reverse('accounts:panel')
        login_url = reverse('accounts:login')
        response = self.client.get(panel_url)
        self.assertRedirects(response, f'{login_url}?next={panel_url}')

    def test_login_usuario_inexistente(self):
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username': 'usuario_inexistente',
                'password': 'ClaveSegura2026!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertTrue(response.context['form'].errors)

    def test_login_contrasena_incorrecta(self):
        User.objects.create_user(
            username='docente_clave',
            password='ClaveCorrecta2026!',
        )
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username': 'docente_clave',
                'password': 'ClaveIncorrecta2026!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertTrue(response.context['form'].errors)

    def test_login_valido(self):
        User.objects.create_user(
            username='docente_valido',
            password='ClaveCorrecta2026!',
        )
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username': 'docente_valido',
                'password': 'ClaveCorrecta2026!',
            },
            follow=True,
        )
        self.assertRedirects(response, reverse('accounts:panel'))
        self.assertIn('_auth_user_id', self.client.session)
        self.assertContains(response, 'docente_valido')

    def test_cierre_sesion_y_nueva_visita_al_panel_pide_autenticacion(self):
        user = User.objects.create_user(
            username='docente_salida',
            password='ClaveCorrecta2026!',
        )
        self.client.force_login(user)

        logout_response = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(logout_response, reverse('accounts:login'))
        self.assertNotIn('_auth_user_id', self.client.session)

        panel_url = reverse('accounts:panel')
        login_url = reverse('accounts:login')
        panel_response = self.client.get(panel_url)
        self.assertRedirects(panel_response, f'{login_url}?next={panel_url}')
