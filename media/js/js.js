$(document).ready(function() {

if (typeof String.prototype.startsWith != 'function') {
  // see below for better implementation!
  String.prototype.startsWith = function (str){
    return this.indexOf(str) == 0;
  };
}

var required_fail = "Campo obligatorio";var numeric_fail = "Este campo solo recibe NUMEROS";
var numericspace_fail = "Este campo solo recibe NUMEROS y ESPACIOS EN BLANCO";
var letters_fail = "Este campo solo recibe LETRAS";
var lettersspace_fail = "Este campo solo recibe LETRAS y ESPACIOS EN BLANCO";
var numericletters_fail = "Este campo solo recibe LETRAS Y NUMEROS";
var numericlettersspace_fail = "Este campo solo recibe LETRAS, NUMEROS Y ESPACIOS EN BLANCO";
var email_fail = "Este campo solo recibe EMAIL validos"

function replace_acentos_upper(texto)
{
    texto=texto.replace(/(À|Á|Â|Ã)/gi,'A');
    texto=texto.replace(/(È|É|Ê)/gi,'E');
    texto=texto.replace(/(Ì|Í|Î)/gi,'I');
    texto=texto.replace(/(Ò|Ó|Ô)/gi,'O');
    texto=texto.replace(/(Ù|Ú|Û)/gi,'U');
    return texto;
}

function replace_acentos(texto)
{
    texto=texto.replace(/(à|á|â|ã)/gi,'a');
    texto=texto.replace(/(è|é|ê)/gi,'e');
    texto=texto.replace(/(ì|í|î)/gi,'i');
    texto=texto.replace(/(ò|ó|ô)/gi,'o');
    texto=texto.replace(/(ù|ú|û)/gi,'u');
    return texto;
}

function text_validate(name){
    $("#div_"+ name +"_error").html("");

    obj_js = $('input[name="'+ name +'"]')

    if (obj_js.val() == undefined){
        obj_js = $('textarea[name="'+ name +'"]')   
    }

    var acentos = false

    if (obj_js.hasClass("upper")){
        if (acentos == true){
            obj_js_val = replace_acentos_upper(obj_js.val().toUpperCase());    
        }
        else{
            obj_js_val = obj_js.val().toUpperCase();
        }
    }
    else{
        if (acentos == true){
            obj_js_val = replace_acentos(obj_js.val());
        }
        else{
            obj_js_val = obj_js.val();   
        }
    }
    
    obj_js.val(obj_js_val)

    if (obj_js.hasClass("required")){
        if (obj_js_val.length == 0){
            $("#div_"+ name +"_error").html(required_fail);
            return 1;
        };
    }; 
     
    if (obj_js.hasClass("numeric")){
        if (!/^(\d)*$/.test(obj_js_val)){
            $("#div_"+ name +"_error").html(numeric_fail);
            return 1;
        }
    };
    
    if (obj_js.hasClass("numericspace")){
        if (!/^(\ |\d)*$/.test(obj_js_val)){
            $("#div_"+ name +"_error").html(numericspace_fail);
            return 1;
        }
    };
    
    if (obj_js.hasClass("letters")){
        if (!/^[a-zA-Z\.\xF1\xD1\xC1\xE1\xC9\xE9\xCD\xED\xD3\xF3\xDA\xFA]*$/.test(obj_js_val)){
            $("#div_"+ name +"_error").html(letters_fail);
            return 1;
        }
    };
    
    if (obj_js.hasClass("lettersspace")){
        if (!/^[a-zA-Z\.\xF1\xD1\xC1\xE1\xC9\xE9\xCD\xED\xD3\xF3\xDA\xFA ]*$/.test(obj_js_val)){
            $("#div_"+ name +"_error").html(lettersspace_fail);
            return 1;
        }
    };
    
    if (obj_js.hasClass("numericletters")){
        if (!/^(\d|[a-zA-Z\.\xF1\xD1\xC1\xE1\xC9\xE9\xCD\xED\xD3\xF3\xDA\xFA]|\.)*$/.test(obj_js_val)){
            $("#div_"+ name +"_error").html(numericletters_fail);
            return 1;
        }
    };
    
    if (obj_js.hasClass("numericlettersspace")){
        if (!/^(\d|[a-zA-Z\.\xF1\xD1\xC1\xE1\xC9\xE9\xCD\xED\xD3\xF3\xDA\xFA]|\.|.)*$/.test(obj_js_val)){
            $("#div_"+ name +"_error").html(numericlettersspace_fail);
            return 1;
        }
    };
    
    if (obj_js.hasClass("email")){
        if (!/^[a-zA-Z0-9\_\-\.]+@[a-zA-Z0-9\_\-]{3,}\.[a-zA-Z]{2,4}(\.[a-zA-Z]{2,4})?$/.test(obj_js_val)){
            $("#div_"+ name +"_error").html(email_fail);
            return 1;
        }
    };

    return 0;         
}

$('#form_script').submit(function(e) {
    try{
    action = $('#form_script').attr('action');
    actionSplit = action.split("/")
    //get all name's of checkbox and radiobutton
    var names = {};
    $('input:radio,input:checkbox').each(function() {
        names[$(this).attr('name')] = true;
    });
    //get only key of dict
    name_option = Object.keys(names);
    
    //get all name's of select
    var selecteds = {};
    $('select').each(function() {
        selecteds[$(this).attr('name')] = true;
    });
    //get only key of dict
    name_selecteds = Object.keys(selecteds);
    
    var texts = {};
    $('input:text,textarea,files').each(function() {
        texts[$(this).attr('name')] = true;
    });
    //get only key of dict
    name_texts = Object.keys(texts);
        
    count = 0;
    //validation for each group name
    $.each(name_option, function(index, value) { 

        if(!$("input[name='"+ value +"']").is(':checked')){
            $("#div_"+ value +"_error").html(required_fail);
            count++;
        }
        else{
            $("#div_"+ value +"_error").html("");
            
            vale = $('input[name='+ value +']:checked').val();

            if ( (value.startsWith("me_")) || (value.startsWith("mi_")) ){
            }
            else{
                proy_salto = actionSplit[2].split("|");
                proy = proy_salto[0];
                salto_nuevo = $("#"+value + "_" + vale).attr("data-salto");
                action_nuevo = '/djpoll/' + proy + "|" + salto_nuevo + "/";
                $("#form_script").get(0).setAttribute('action', action_nuevo); 
            }
            
        }
        
    });

    $.each(name_selecteds, function(index, value) { 
        if(!$("select[name='"+ value +"']").val().length > 0){
            $("#div_"+ value +"_error").html(required_fail);
            count++;
        }
        else{
            $("#div_"+ value +"_error").html("");

            vale = $("select[name='"+ value +"']").val();

            proy_salto = actionSplit[2].split("|")
            proy = proy_salto[0]
            salto_nuevo = $("#"+value + "_" + vale).attr("data-salto")
            action_nuevo = '/djpoll/' + proy + "|" + salto_nuevo + "/"

            $("#form_script").get(0).setAttribute('action', action_nuevo); 
            
        }
        
    });

     $.each(name_texts, function(index, value) {
        count += text_validate(value);
     });
    
    if (count > 0){
        e.preventDefault();
    }

    }catch(er){alert(er)}
})

});