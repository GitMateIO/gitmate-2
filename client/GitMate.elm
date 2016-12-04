module GitMate exposing (..)

import Bootstrap.Buttons exposing (..)
import Bootstrap.Grid exposing (..)
import Bootstrap.Navbar exposing (..)
import Bootstrap.Page exposing (..)
import Bootstrap.Wells exposing (..)

import Html exposing (..)
import Html.Attributes exposing (..)


main =
  containerFluid
    [ navbar DefaultNavbar []
        [ containerFluid
            [ navbarHeader []
                [ navbarBrand []
                    [ text "Gitmate" ]
                ]
            , navbarList NavbarNav NavbarDefault []
                [ li []
                    [ a []
                        [ text "Plugins" ]
                    ]
                ]
            ]
        ]
    , jumbotron []
        [ h1 []
            [ text "Hey Elmana!" ]
        , btn BtnPrimary [] [] []
            [ text "GitLab" ]
        ]
    ]
