

function termClicked(termElement)
{
    termChildren = termElement.getElementsByClassName("jeffTermPopup");
    popupElement = termChildren[0];
    if (popupElement.style.opacity == 0)
    {
        popupElement.style.opacity = "1.0";
    }
    else
    {
        popupElement.style.opacity = "0.0";
    }
}

function termClosed(popupElement)
{
    popupElement.style.opacity = "0.0";
}