from django.db import models
from django import forms
from django.db.models.signals import post_save

from utils.models import BaseModel
from operador.models import Operator
from category.models import Category
from operator_setting.models import KeyValueSystem 

class Ostype(BaseModel):
    operator = models.ForeignKey('operador.Operator', null=False, blank=False ,on_delete=models.CASCADE)
    name     =  models.CharField(max_length=100)
    color    = models.CharField(max_length=100)
    tag      = models.CharField(max_length=50)
    sequential_id = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return f"{self.name} - {self.operator.name}"
    
    def get_text_history(self, updater, change, change_aux):
    
        if change.field == 'operator':
            operador = Operator.objects.get(ID=change.old)
            return f"El usuario {updater} modifico el operadpr de {operador.name} a {self.operator.name}."
        
        return None

    def _validate_sequential_id (self):
        id = Ostype.objects.filter(operator=self.operator).count()+1
        self.sequential_id = id 

    def _validate_name(self):
        name = self.name
        name_spaces = name.replace(" ", "")
        if name_spaces.isalpha() == False:
            raise forms.ValidationError('Error: Nombre tiene caracteres especiales.')

    def save(self, *args, **kwargs):
        #self._validate_name()
        if self.ID == None : 
            self._validate_sequential_id()
        super(Ostype, self).save(*args, **kwargs)
        
    class Meta:
            verbose_name='OStype'
            verbose_name_plural='OStypes'


def asociar_os(sender, instance, **kwargs):

    qs = KeyValueSystem.objects.filter(name='force_signal_asociar_os')
    if qs.count() > 0:
        force_signal = True
    else:
        force_signal = False

    if kwargs.get('created') is True or force_signal:
        
        ostype_1 = Ostype.objects.create(operator=instance,name='Visita Técnica Cliente sin servicio',
                                         color='#fd7d48', tag="Naranja")
        ostype_2 = Ostype.objects.create(operator=instance,name='Visita Técnica Cliente con servicio',
                                         color='#f5c43c', tag="Amarillo")
        ostype_3 = Ostype.objects.create(operator=instance,name='Migración',
                                         color='#003cb9', tag="Azul")
        ostype_4 = Ostype.objects.create(operator=instance,name='Instalación',
                                         color='#8fd14f', tag="Verde")
        ostype_5 = Ostype.objects.create(operator=instance,name='Retiro de equipo',
                                         color='#6c6c6b', tag="Gris")
        ostype_6 = Ostype.objects.create(operator=instance,name='Traslado de servicio',
                                         color='#860ac5', tag="Morado")
        
        #Ostype_1
        Category.objects.create(
                                    name="No hay acceso al equipo", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Fotografía de la etiqueta con serie del equipo"
                                                        },
                                                        {
                                                            "img_name": "Fotografía del equipo instalado"
                                                        }, 
                                                        {
                                                            "img_name": "Test de Velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Se cambió el equipo?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_1
                                )

        Category.objects.create(
                                    name="Corte de fibra de la roseta", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Fotografía de la etiqueta con serie del equipo"
                                                        },
                                                        {
                                                            "img_name": "Fotografía del equipo instalado"
                                                        }, 
                                                        {
                                                            "img_name": "Test de Velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Se cambió el equipo?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_1
                                )

        Category.objects.create(
                                    name="Corte de fibra en la acometida.", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Fotografía de la etiqueta con serie del equipo"
                                                        },
                                                        {
                                                            "img_name": "Fotografía del equipo instalado"
                                                        }, 
                                                        {
                                                            "img_name": "Test de Velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Se cambió el equipo?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                            },
                                    os_type=ostype_1
                                )

        Category.objects.create(
                                    name="Equipo no enciende.", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        { 
                                                            "img_name": "Fotografía de la etiqueta con serie del equipo"
                                                        },
                                                        {
                                                            "img_name": "Fotografía del equipo instalado"
                                                        }, 
                                                        {
                                                            "img_name": "Test de Velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Se cambió el equipo?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_1
                                )

        #Ostype_2
        Category.objects.create(
                                    name="No le llegan los megas", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Fotografía de la etiqueta con serie del equipo"
                                                        },
                                                        {
                                                            "img_name": "Fotografía del equipo instalado"
                                                        }, 
                                                        {
                                                            "img_name": "Test de Velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Se cambió el equipo?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_2
                                )

        Category.objects.create(
                                    name="Cablear smart TV", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Fotografía del dispositivo cableado"
                                                        },
                                                        {
                                                            "img_name": "Fotografía del test de velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Se cableó la consola o SmarTV?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_2
                                )

        Category.objects.create(
                                    name="Cablear consola", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Fotografía del dispositivo cableado"
                                                        },
                                                        {
                                                            "img_name": "Fotografía del test de velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Se cableó la consola o SmarTV?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_2
                                )

        Category.objects.create(
                                    name="Cambio de equipo", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Fotografía del equipo instalado"
                                                        }, 
                                                        {
                                                            "img_name": "Fotografía de la etiqueta con serie del equipo"
                                                        },
                                                        {
                                                            "img_name": "Fotografía del test de velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Se cambió el equipo? ",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_2
                                )

        #Ostype_3
        Category.objects.create(
                                    name="UTP a Fibra", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        { 
                                                            "img_name": "Foto medidor potencia en la caja del shaft"
                                                        }, 
                                                        {
                                                            "img_name": "Foto Cable drop de cliente etiquetado."
                                                        }, 
                                                        {
                                                            "img_name": "Foto panorámica del shaft."
                                                        }, 
                                                        {
                                                            "img_name": "Foto potencia en la roseta"
                                                        }, 
                                                        {
                                                            "img_name": "Foto serial de equipo"
                                                        }, 
                                                        {
                                                            "img_name": "Foto Panorámica de la instalación"
                                                        }, 
                                                        {
                                                            "img_name": "Foto test de velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_3
                                )

        Category.objects.create(
                                    name="Antena a Fibra", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Foto medidor potencia en la caja del shaft"
                                                        }, 
                                                        {
                                                            "img_name": "Foto Cable drop de cliente etiquetado."
                                                        },
                                                        {
                                                            "img_name": "Foto panorámica del shaft."
                                                        }, 
                                                        {
                                                            "img_name": "Foto potencia en la roseta"
                                                        }, 
                                                        {
                                                            "img_name": "Foto serial de equipo"
                                                        }, 
                                                        {
                                                            "img_name": "Foto Panorámica de la instalación"
                                                        }, 
                                                        {
                                                            "img_name": "Foto test de velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_3
                                )

        #Ostype_4
        Category.objects.create(
                                    name="UTP", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Foto switch en shaft "
                                                        }, 
                                                        {
                                                            "img_name": "Foto cable utp del cliente etiquetado."
                                                        },
                                                        {
                                                            "img_name": "Foto panorámica del shaft."
                                                        }, 
                                                        {
                                                            "img_name": "Foto serial de equipo."
                                                        }, 
                                                        {
                                                            "img_name": "Foto Panorámica de la instalación"
                                                        },
                                                        {
                                                            "img_name": "Foto test de velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_4
                                )

        Category.objects.create(
                                    name="Antena", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Foto switch en shaft "
                                                        }, 
                                                        { 
                                                            "img_name": "Foto cable utp del cliente etiquetado."
                                                        },
                                                        {
                                                            "img_name": "Foto panorámica del shaft."
                                                        }, 
                                                        {
                                                            "img_name": "Foto serial de equipo."
                                                        }, 
                                                        {
                                                            "img_name": "Foto Panorámica de la instalación"
                                                        },
                                                        {
                                                            "img_name": "Foto test de velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_4)

        Category.objects.create(
                                    name="Fibra", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name":"Foto medidor potencia en la caja del shaft"
                                                        },
                                                        {
                                                            "img_name": "Foto Cable drop de cliente etiquetado."
                                                        },
                                                        {
                                                            "img_name": "Foto panorámica del shaft."
                                                        },
                                                        {
                                                            "img_name": "Foto potencia en la roseta"
                                                        },
                                                        {
                                                            "img_name": "Foto serial de equipo"
                                                        },
                                                        {
                                                            "img_name": "Foto Panorámica de la instalación"
                                                        },
                                                        {
                                                            "img_name": "Foto test de velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_4
                                )

        #Ostype_5
        Category.objects.create(
                                    name="Cliente Moroso - Rappi", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Fotografía general del equipo con transformador"
                                                        }, 
                                                        {
                                                            "img_name": "Fotografía de la etiqueta con serie del equipo."
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_5
                                )

        Category.objects.create(
                                    name="Cliente Moroso - Técnico", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Fotografía general del equipo con transformador"
                                                        }, 
                                                        {
                                                            "img_name": "Fotografía de la etiqueta con serie del equipo."
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_5
                                )

        Category.objects.create(
                                    name="Cliente Por retirar - Rappi", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Fotografía general del equipo con transformador"
                                                        }, 
                                                        {
                                                            "img_name": "Fotografía de la etiqueta con serie del equipo."
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_5
                                )

        Category.objects.create(
                                    name="Cliente Por retirar - Técnico", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Fotografía general del equipo con transformador"
                                                        },
                                                        {
                                                            "img_name": "Fotografía de la etiqueta con serie del equipo."
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_5
                                )

        #Ostype_6
        Category.objects.create(
                                    name="Traslado", 
                                    duration=60, 
                                    imgs={
                                            "value":[
                                                        {
                                                            "img_name": "Foto medidor potencia en la caja del shaft"
                                                        }, 
                                                        {
                                                            "img_name": "Foto Cable drop de cliente etiquetado."
                                                        }, 
                                                        {
                                                            "img_name": "Foto panorámica del shaft."
                                                        }, 
                                                        {
                                                            "img_name": "Foto potencia en la roseta"
                                                        }, 
                                                        {
                                                            "img_name": "Foto serial de equipo"
                                                        }, 
                                                        {
                                                            "img_name": "Foto Panorámica de la instalación"
                                                        }, 
                                                        {
                                                            "img_name": "Foto test de velocidad"
                                                        }
                                                    ]
                                            }, 
                                    questions={
                                                "value":[
                                                            {
                                                                "question": "¿Cliente Conforme?",
                                                                "kind": 1
                                                            },
                                                            {
                                                                "question": "Comentarios adicionales",
                                                                "kind": 2
                                                            }
                                                        ]
                                                },
                                    os_type=ostype_6
                                )

post_save.connect(asociar_os, sender=Operator)  
