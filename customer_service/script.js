$(function () {
    $('select').select2();
});

// Function to fetch language data
async function fetchLanguageData(lang) {
    //const response = await fetch(`languages/${lang}.json`);
    //return response.json();
    /*$.getJSON( `languages/${lang}.json`, function( json ) {
        return json;
    });*/

    return lang === 'fr' ? fr : en;
  }
  
  // Function to set the language preference
  function setLanguagePreference(lang) {
    localStorage.setItem('language', lang);
    location.reload();
  }
  
  // Function to update content based on selected language
  function updateContent(langData) {
    document.querySelectorAll('[data-i18n]').forEach(element => {
      const key = element.getAttribute('data-i18n');
      if(element.nodeName === 'INPUT' || element.nodeName === 'LABEL' || element.nodeName === 'H2' || element.nodeName === 'P') {
        element.textContent = langData[key];
      }
      if(element.nodeName === 'OPTION') {
        element.textContent = langData[key];
        element.setAttribute("value", langData[key]);
      } 
      if(element.nodeName === 'OPTGROUP') {
        element.setAttribute("label", langData[key]);
      }

      if(element.nodeName === 'SELECT') {
        element.setAttribute("title", langData[key]);
      }
    });
  }
  
  // Function to change language
  async function changeLanguage(lang) {
    await setLanguagePreference(lang);
    
    const langData = await fetchLanguageData(lang);
    updateContent(langData);
  }  
  
  // Call updateContent() on page load
  window.addEventListener('DOMContentLoaded', async () => {
    const userPreferredLanguage = localStorage.getItem('language') || 'fr';
    const langData = await fetchLanguageData(userPreferredLanguage);
    updateContent(langData);
  });
 
 
  