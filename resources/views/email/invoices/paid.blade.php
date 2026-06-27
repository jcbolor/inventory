@component('email.template.master', ['design' => 'light', 'settings' => $settings])
    @slot('header')
        @include('email.components.header', ['logo' => asset('images/logo.png')])
    @endslot

    <h1>Payment for your invoice has been completed!</h1>
    <p>We want to inform you that payment was completed for your invoice.</p>

    <a href="https://bizlabitsolutions.com" target="_blank" class="button">Visit BizLab IT Solutions</a>
@endcomponent
