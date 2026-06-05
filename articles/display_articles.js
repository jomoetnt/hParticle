let pageNum = 1;
let pageElements = document.getElementsByClassName("jeffArticleListPage");

function updatePages()
{
    if (pageNum < 1)
    {
        pageNum = 1;
    }
    else if (pageNum == 1)
    {
        document.getElementById("PrevButton").style.display = "none";
    }
    else
    {
        document.getElementById("PrevButton").style.display = "block";
    }
    if (pageNum > pageElements.length)
    {
        pageNum = pageElements.length;
    }
    else if (pageNum == pageElements.length)
    {
        document.getElementById("NextButton").style.display = "none";
    }
    else
    {
        document.getElementById("NextButton").style.display = "block";
    }
    for (let i = 0; i < pageElements.length; i++)
    {
        console.log(pageElements[i].id);
        if (pageElements[i].id != 'page_' + pageNum)
        {
            pageElements[i].style.display = "none";
        }
        else
        {
            pageElements[i].style.display = "block";
        }
    }
    document.getElementById("pageNumDisplay").textContent = 'Showing Page ' + pageNum + ' of ' + pageElements.length;
}

function changePage(delta)
{
    pageNum += delta;
    updatePages();
}