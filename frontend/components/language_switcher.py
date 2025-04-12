import streamlit as st

def language_switcher(i18n_manager):
    """
    Hiển thị nút chuyển đổi ngôn ngữ trong Streamlit
    
    Args:
        i18n_manager: Instance của I18nManager để quản lý ngôn ngữ
    """
    available_locales = i18n_manager.get_all_locales()
    
    locale_names = {
        "vi": "Tiếng Việt 🇻🇳",
        "en": "English 🇬🇧"
    }

    locale_options = [locale_names.get(locale, locale) for locale in available_locales]
    
    current_locale_name = locale_names.get(i18n_manager.current_locale, i18n_manager.current_locale)
    current_index = available_locales.index(i18n_manager.current_locale)

    selected_locale_name = st.selectbox(
        "",
        options=locale_options,
        index=current_index,
        key="language_selector"
    )
    
    selected_index = locale_options.index(selected_locale_name)
    selected_locale = available_locales[selected_index]
    
    if selected_locale != i18n_manager.current_locale:
        i18n_manager.set_locale(selected_locale)
        st.experimental_rerun() 