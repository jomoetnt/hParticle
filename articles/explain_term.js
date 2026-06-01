

function termClicked(termElement)
{
    termChildren = termElement.getElementsByClassName("jeffTermPopup");
    popupElement = termChildren[0];

    triangleElement = popupElement.getElementsByClassName("jeffTriangle")[0];

    if (popupElement.style.opacity == 0)
    {
        popupElement.style.opacity = "1.0";

        idealPosition = termElement.getBoundingClientRect().left + termElement.getBoundingClientRect().width / 2 - popupElement.getBoundingClientRect().width / 2;
        if (idealPosition < 0)
        {
            triangleElement.style.left = idealPosition + "px";
            popupElement.style.left = "0px";
        }
        else if (idealPosition + popupElement.getBoundingClientRect().width < document.body.getBoundingClientRect().width)
        {
            triangleElement.style.left = "0px";
            popupElement.style.left = idealPosition + "px";
        }
        else
        {
            triangleElement.style.left = (window.innerWidth - termElement.getBoundingClientRect().left) + "px";
            popupElement.style.left = document.body.getBoundingClientRect().width - popupElement.getBoundingClientRect().width + "px";
        }
        popupElement.style.top = termElement.getBoundingClientRect().bottom + "px";
    }
    else
    {
        hideElement(popupElement);
    }
}

function termClosed(popupElement)
{
    hideElement(popupElement);
}

function hideElement(element)
{
    element.style.opacity = "0.0";
    setTimeout(banishElement, 500, element);
}

function banishElement(element)
{
    if (element.style.opacity == 1)
        return;
    element.style.left = "-500px";
    element.style.top = "-500px";
}