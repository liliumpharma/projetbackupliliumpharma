$(document).ready(function(){



    // const phone_input=document.querySelector("#id_userprofile-0-telephone").parentElement.parentElement.parentElement
    // const address_input=document.querySelector("#id_userprofile-0-adresse").parentElement.parentElement.parentElement
    // const gender_input=document.querySelector("#id_userprofile-0-gender").parentElement.parentElement.parentElement
    // const birth_date_input=document.querySelector("#id_userprofile-0-date_of_birth").parentElement.parentElement.parentElement
    // const situation_input=document.querySelector("#id_userprofile-0-situation").parentElement.parentElement.parentElement
    // const entry_date_input=document.querySelector("#id_userprofile-0-entry_date").parentElement.parentElement.parentElement
    // const CNAS_input=document.querySelector("#id_userprofile-0-CNAS").parentElement.parentElement.parentElement
    // const bank_name_input=document.querySelector("#id_userprofile-0-bank_name").parentElement.parentElement.parentElement
    // const bank_account_input=document.querySelector("#id_userprofile-0-bank_account").parentElement.parentElement.parentElement
    // const salary_input=document.querySelector("#id_userprofile-0-salary").parentElement.parentElement.parentElement
    // const conge_input=document.querySelector("#id_userprofile-0-conge").parentElement.parentElement.parentElement
    // const job_name=document.querySelector("#id_userprofile-0-job_name").parentElement.parentElement.parentElement
    
    
    // $("#personal-info-tab").find(".card-body").append(address_input)
    // $("#personal-info-tab").find(".card-body").append(situation_input)
    // $("#personal-info-tab").find(".card-body").append(birth_date_input)
    // $("#personal-info-tab").find(".card-body").append(gender_input)
    // $("#personal-info-tab").find(".card-body").append(phone_input)
    // $("#personal-info-tab").find(".card-body").append(entry_date_input)
    // $("#personal-info-tab").find(".card-body").append(CNAS_input)
    // $("#personal-info-tab").find(".card-body").append(bank_name_input)
    // $("#personal-info-tab").find(".card-body").append(bank_account_input)
    // $("#personal-info-tab").find(".card-body").append(salary_input)
    // $("#personal-info-tab").find(".card-body").append(conge_input)
    // $("#personal-info-tab").find(".card-body").append(job_name)


    $('#add_id_userprofile-0-sectors').after('\
    <div id="remove_all_sectors" style="display: inline-block; background-color: red; border-radius: 7px; padding: 2px; cursor: pointer">\
        Tout Retirer\
    </div>')

    $('#remove_all_sectors').click(()=>{
        data = []
        $('#id_userprofile-0-sectors').val(data)
        $('#id_userprofile-0-sectors').trigger('change')
    })

    $('#add_id_userprofile-0-sectors').after('\
    <div id="add_all_sectors" style="display: inline-block; background-color: green; border-radius: 7px; padding: 2px; cursor: pointer">\
        Tout Ajouter\
    </div>')

    $('#add_all_sectors').click(()=>{
        data = []

        for(const item of $('#id_userprofile-0-sectors').find('option')){
            data.push(item.value)
        }

        $('#id_userprofile-0-sectors').val(data)
        $('#id_userprofile-0-sectors').trigger('change')
    })

    
    
})

